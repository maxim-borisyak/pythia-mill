from pythiamill.utils import launch_pythia, pythia_worker
from pythiamill.utils import STDetector, SDetector

import numpy as np
import multiprocessing as mp
from multiprocessing import Process

__all__ = [
  'PythiaMill',
  'pythia_blade'
]

def pythia_blade(detector_factory, command_queue, queue, options, batch_size=1):
  import sys
  import os
  sys.stdout = open(os.devnull, 'w')
  sys.stderr = open(os.devnull, 'w')

  detector_instance = detector_factory()

  event_size = detector_instance.event_size()
  buffer = np.ndarray(shape=(batch_size, event_size), dtype='float32')

  pythia = launch_pythia(options)

  while True:
    c = command_queue.get(block=True)
    if c is None:
      command_queue.task_done()
      queue.put(None, block=True)
      break

    pythia_worker(detector_instance, pythia, buffer)
    command_queue.task_done()
    queue.put(buffer.copy(), block=True)

def PythiaBlade(detector_factory, command_queue, queue, options, batch_size=1):
  return Process(
    target=pythia_blade,
    args=(detector_factory, command_queue, queue, options, batch_size)
  )


class PythiaMill(object):
  def __init__(self, detector_factory, options, batch_size=16,
               cache_size=None, n_workers=4):
    self.cache_size = cache_size if cache_size is not None else n_workers * 2

    ctx = mp.get_context('spawn')

    self.command_queue = ctx.JoinableQueue()
    self.queue = ctx.JoinableQueue()

    self.fill_size = 0

    self.processes = [
      ctx.Process(
        target=pythia_blade,
        kwargs=dict(
          detector_factory=detector_factory,
          command_queue=self.command_queue,
          queue=self.queue,
          options=options,
          batch_size=batch_size
        )
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