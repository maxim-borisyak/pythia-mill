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

    while not self.exit_event.is_set():
      pythia_worker(pythia, buffer)
      queue.put(buffer.copy(), block=True)


class PythiaMill(object):
  def __init__(self, options, event_shape=(4, 128, 128), batch_size=16,
               cache_size=128, buffer_size=None, n_workers=4, minimum_size_scale_factor=1.5):
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

    self.event_shape = event_shape

    self.minimum_size = 0
    self.minimum_size_scale_factor = minimum_size_scale_factor
    self.update_i = 0

    for p in self.processes:
      p.start()

  def wait_unit(self, n):
    assert self.X is not None, 'current instance does not have buffer'

    if n >= self.X.shape[0]:
      n = self.X.shape[0]

    counter = 0
    while self.fill_size < n:
      batch = self.queue.get(block=True)
      counter += 1
      from_i = self.fill_size
      to_i = from_i + batch.shape[0]

      if to_i > self.X.shape[0]:
        batch = batch[:(self.X.shape[0] - self.fill_size)]
        to_i = self.X.shape[0]

      self.X[from_i:to_i] = batch
      self.fill_size += batch.shape[0]

    return counter

  def update_filled(self, max_updates = 32):
    for i in range(max_updates):
      try:
        batch = self.queue.get_nowait()
      except:
        break

      indx = np.arange(self.update_i, self.update_i + batch.shape[0]) % self.X.shape[0]

      self.X[indx] = batch
      self.update_i += batch.shape[0]
      self.update_i %= self.X.shape[0]


  def fill(self, max_updates = 32):
    for i in range(max_updates):
      if self.fill_size >= self.X.shape[0]:
        return

      try:
        batch = self.queue.get_nowait()
      except:
        break

      from_i = self.fill_size
      to_i = from_i + batch.shape[0]

      if to_i > self.X.shape[0]:
        batch = batch[:(self.X.shape[0] - self.fill_size)]
        to_i = self.X.shape[0]

      print 'filling from %d to %d'
      self.X[from_i:to_i] = batch
      self.fill_size += batch.shape[0]

  def sample_unbuffered(self, batch_size=32):
    X = np.ndarray(shape=(batch_size,) + self.event_shape)

    i = 0
    while i < X.shape[0]:
      batch = self.queue.get(block=True)

      to_i = i + batch.shape[0]

      if to_i > X.shape[0]:
        batch = batch[:(X.shape[0] - i)]
        to_i = X.shape[0]

      X[i:to_i] = batch
      i += batch.shape[0]

    return X

  def sample_filled(self, batch_size=32, perform_fill=True, max_updates = 32):
    if perform_fill:
      self.update_filled(max_updates)

    indx = np.random.randint(0, self.fill_size, size=batch_size)
    return self.X[indx]

  def sample_filling(self, batch_size=32, perform_fill=True, max_updates = 32):
    self.minimum_size = min([
      self.minimum_size + int(batch_size * self.minimum_size_scale_factor),
      self.X.shape[0]
    ])

    updates = self.wait_unit(self.minimum_size)

    if perform_fill and updates < max_updates:
      self.fill(max_updates - updates)

    indx = np.random.randint(0, self.fill_size, size=batch_size)
    return self.X[indx]

  def sample(self, batch_size=32, perform_fill=True, max_updates = 32):
    if self.X is None:
      return self.sample_unbuffered(batch_size)
    elif self.fill_size >= self.X.shape[0]:
      return self.sample_filled(batch_size=batch_size, perform_fill=perform_fill, max_updates=max_updates)
    else:
      return self.sample_filling(batch_size=batch_size, perform_fill=perform_fill, max_updates=max_updates)

  def terminate(self):
    if self.processes is None:
      return

    for p in self.processes:
      p.terminate()

    self.processes = None