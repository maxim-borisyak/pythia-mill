from utils import launch_pythia, pythia_worker

import numpy as np
from multiprocessing import Process, Queue, Event
from multiprocessing import Manager

__all__ = [
  'PythiaMill'
]

class PythiaBlade(Process):
  def __init__(self, detector, command_queue, queue, options, event_size=4 * 128 * 128, batch_size=1):
    super(PythiaBlade, self).__init__()

    self.detector = detector

    self.command_queue = command_queue
    self.queue = queue

    self.options = options
    self.buffer = np.ndarray(shape=(batch_size, event_size), dtype='float32')

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
        self.queue.put(None, block=True)
        break

      pythia_worker(self.detector, pythia, buffer)
      self.command_queue.task_done()
      self.queue.put(buffer.copy(), block=True)


class PythiaMill(object):
  def __init__(self, detector, options, event_size=3 * 128 * 128, batch_size=16,
               cache_size=None, n_workers=4):
    self.cache_size = cache_size if cache_size is not None else n_workers * 2

    self.manager = Manager()
    self.command_queue = self.manager.JoinableQueue()
    self.queue = self.manager.JoinableQueue()

    self.fill_size = 0

    self.processes = [
      PythiaBlade(
        detector=detector,
        command_queue=self.command_queue, queue=self.queue,
        options=options, event_size=event_size,
        batch_size=batch_size
      )
      for _ in range(n_workers)
    ]

    for p in self.processes:
      p.start()

    for _ in range(self.cache_size):
      self.command_queue.put(1)

  def __iter__(self):
    return self

  def __next__(self):
    return self.sample()

  def next(self):
    return self.sample()

  def sample(self):
    batch = self.queue.get(block=True)
    self.queue.task_done()
    self.command_queue.put(1)
    return batch

  def terminate(self):
    if self.processes is None:
      return

    for p in self.processes:
      p.terminate()

    self.processes = None

  def __del__(self):
    self.terminate()

  def shutdown(self):
    if self.processes is None:
      return

    for _ in self.processes:
      self.command_queue.send(None)

    stopped = 0
    for i in range(self.cache_size):
      c = self.queue.get(block=True)
      self.queue.task_done()

      if c is None:
        stopped += 1

      if stopped >= len(self.processes):
        return

    self.terminate()
    self.processes = None