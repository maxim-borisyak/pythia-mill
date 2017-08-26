from utils import launch_pythia, pythia_worker

import numpy as np
from multiprocessing import Process, Queue, Event
from multiprocessing import Manager

__all__ = [
  'PythiaMill'
]

class PythiaBlade(Process):
  def __init__(self, command_queue, queue, options, event_shape=(4, 128, 128), batch_size=1):
    super(PythiaBlade, self).__init__()

    self.command_queue = command_queue
    self.queue = queue

    self.options = options
    self.buffer = np.ndarray(shape=(batch_size, ) + event_shape, dtype='float32')

  def run(self):
    import sys
    import os

    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    buffer = self.buffer
    pythia = launch_pythia(self.options)

    while True:
      c = self.command_queue.get(block=True)
      if c is None:
        self.command_queue.task_done()
        break

      pythia_worker(pythia, buffer)
      self.command_queue.task_done()
      self.queue.put(buffer.copy(), block=True)


class PythiaMill(object):
  def __init__(self, options, event_shape=(4, 128, 128), batch_size=16,
               cache_size=128, n_workers=4):
    self.cache_size = cache_size

    self.manager = Manager()
    self.command_queue = self.manager.JoinableQueue()
    self.queue = self.manager.JoinableQueue()

    self.fill_size = 0

    self.processes = [
      PythiaBlade(
        command_queue=self.command_queue, queue=self.queue,
        options=options, event_shape=event_shape, batch_size=batch_size
      )
      for _ in range(n_workers)
    ]

    for p in self.processes:
      p.start()

    for _ in self.processes:
      self.command_queue.put(1)

  def sample(self):
    batch = self.queue.get(block=True)
    self.queue.task_done()
    self.command_queue.put(1)
    return batch

  def terminate(self):
    for p in self.processes:
      p.terminate()

    self.processes = None