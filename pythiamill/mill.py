from utils import launch_pythia, pythia_worker

import numpy as np
from multiprocessing import Process, Queue, Event

__all__ = [
  'PythiaMill'
]

class PythiaBlade(Process):
  def __init__(self, queue, options, event_shape=(4, 128, 128), batch_size=1):
    super(PythiaBlade, self).__init__()
    self.queue = queue
    self.exit_event = Event()
    self.options = options
    self.buffer = np.ndarray(shape=(batch_size, ) + event_shape, dtype='float32')

  def run(self):
    import sys
    import os

    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    buffer = self.buffer
    pythia = launch_pythia(self.options)
    queue = self.queue

    def write(event, timeout=0.1):
      try:
        queue.put(event, block=True, timeout=timeout)
        return True
      except:
        return False

    while not self.exit_event.is_set():
      pythia_worker(pythia, buffer)
      copy = buffer.copy()

      while not (self.exit_event.is_set() or write(copy)):
        pass

    del pythia

  def stop(self):
    print "Shutdown initiated"
    self.exit_event.set()


class PythiaMill(object):
  def __init__(self, options, event_shape=(4, 128, 128), batch_size=16, cache_size=128, buffer_size=None, n_workers=4):
    self.queue = Queue(maxsize=cache_size)
    if buffer_size is not None:
      self.X = np.ndarray(shape=(buffer_size, ) + event_shape, dtype='float32')
    else:
      self.X = None

    self.fill_size = 0

    self.processes = [
      PythiaBlade(queue=self.queue, options=options, event_shape=event_shape, batch_size=batch_size)
      for _ in range(n_workers)
    ]

    for p in self.processes:
      p.start()

  def wait_unit(self, n):
    assert self.X is not None, 'current instance does not have buffer'
    assert n <= self.X.shape[0], 'wait more events than buffer size?'

    while self.fill_size < n:
      batch = self.queue.get(block=True)
      from_i = self.fill_size
      to_i = from_i + batch.shape[0]

      if to_i > self.X.shape[0]:
        batch = batch[:(self.X.shape[0] - self.fill_size)]
        to_i = self.X.shape[0]

      self.X[from_i:to_i] = batch
      self.fill_size += batch.shape[0]

    if self.fill_size >= self.X.shape[0]:
      self.terminate()

  def fill(self):
    while self.fill_size < self.X.shape[0]:
      try:
        batch = self.queue.get_nowait()
      except:
        break

      from_i = self.fill_size
      to_i = from_i + batch.shape[0]

      if to_i > self.X.shape[0]:
        batch = batch[:(self.X.shape[0] - self.fill_size)]
        to_i = self.X.shape[0]

      self.X[from_i:to_i] = batch
      self.fill_size += batch.shape[0]

    if self.fill_size >= self.X.shape[0]:
      self.terminate()

  def sample(self, batch_size=32, perform_fill=True):
    self.wait_unit(batch_size)

    if perform_fill:
      self.fill()

    print self.fill_size

    indx = np.random.randint(0, self.fill_size, size=batch_size)
    return self.X[indx]

  def terminate(self):
    if self.processes is None:
      return

    for p in self.processes:
      p.stop()
      p.terminate()

    self.processes = None





