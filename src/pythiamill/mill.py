from pythiamill.utils import launch_pythia, pythia_worker

import numpy as np
import multiprocessing as mp
from multiprocessing import Process, current_process

import os
import sys
import signal

__all__ = [
  'PythiaMill',
  'CachedPythiaMill',
  'ParametrizedPythiaMill',
  'pythia_blade',
]

def pythia_blade(detector_factory, command_queue, queue, options, batch_size=1):
  import sys
  import os

  if current_process().name != 'MainProcess':
    ### These two lines can be very dangerous
    ### if this function is executed in the main process.
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    pass

  detector_instance = detector_factory()

  event_size = detector_instance.event_size()
  buffer = np.ndarray(shape=(batch_size, event_size), dtype='float32')
  pythia = launch_pythia(options)

  while True:
    args = command_queue.get(block=True)
    if args is None:
      command_queue.task_done()
      queue.put(None, block=True)
      break

    try:
      pythia_worker(detector_instance, pythia, buffer, args)
      command_queue.task_done()
      queue.put((args, buffer.copy()), block=True)
    except Exception as e:
      command_queue.task_done()
      queue.put((args, e), block=True)



def PythiaBlade(detector_factory, command_queue, queue, options, batch_size=1):
  return Process(
    target=pythia_blade,
    args=(detector_factory, command_queue, queue, options, batch_size)
  )

class PythiaMillBase(object):
  def __init__(self, detector_factory, options, batch_size=16,
               n_workers=4, seed=None):

    if seed is not None:
      if any([ 'Random:seed' in option for option in options]):
        import warnings
        warnings.warn('randomize_seed is turned off as Pythia options contain seed settings.')
        seed = None
    else:
      if not any(['Random:seed' in option for option in options]):
        import warnings
        warnings.warn('`seed` argument is not specified and Pythia options does not contain `Random:seed` options. '
                      'This may result in duplicating samples.')


    if seed is not None:
      import random
      random.seed(seed)
      seeds = set()

      while len(seeds) < n_workers:
        seeds.add(random.randrange(1, 900000000))

      seeds = list(seeds)
      random.shuffle(seeds)

    ctx = mp.get_context('spawn')

    self.command_queue = ctx.JoinableQueue()
    self.queue = ctx.JoinableQueue()

    self.processes = [
      ctx.Process(
        target=pythia_blade,
        kwargs=dict(
          detector_factory=detector_factory,
          command_queue=self.command_queue,
          queue=self.queue,
          options=options if seed is None else (options + ['Random:setSeed=on', 'Random:seed=%d' % seeds[i]]),
          batch_size=batch_size
        )
      )
      for i in range(n_workers)
    ]

    for p in self.processes:
      p.start()

  def terminate(self):
    if self.processes is None:
      return

    for p in self.processes:
      try:
        os.kill(p.pid, signal.SIGKILL)
      except Exception as e:
        print('Failed to stop pythia blade (pid %d), reason: %s' % (p.pid, e))

    self.processes = None

  def __del__(self):
    self.terminate()

  def shutdown(self):
    if self.processes is None:
      return

    for _ in self.processes:
      self.command_queue.send(None)

    stopped = 0
    while True:
      c = self.queue.get(block=True)
      self.queue.task_done()

      if c is None:
        stopped += 1

      if stopped >= len(self.processes):
        break

    self.terminate()
    self.processes = None


class CachedPythiaMill(PythiaMillBase):
  def __init__(self, detector_factory, options, detector_args=(), batch_size=16,
               cache_size=None, n_workers=4, seed=None):
    
    super(CachedPythiaMill, self).__init__(
      detector_factory=detector_factory,
      options=options,
      batch_size=batch_size,
      n_workers=n_workers,
      seed=seed
    )

    self.cache_size = cache_size
    self.detector_args = detector_args

    for _ in range(self.cache_size):
      self.command_queue.put(self.detector_args)

  def __iter__(self):
    return self

  def __next__(self):
    return self.sample()

  def next(self):
    return self.sample()

  def sample(self):
    if self.processes is None:
      raise ValueError('Mill has already been stopped!')

    _, batch = self.queue.get(block=True)
    self.queue.task_done()
    self.command_queue.put(self.detector_args)
    return batch


class ParametrizedPythiaMill(PythiaMillBase):
  def __init__(self, detector_factory, options, batch_size=16, n_workers=4, seed=None):
    super(ParametrizedPythiaMill, self).__init__(
      detector_factory=detector_factory,
      options=options,
      batch_size=batch_size,
      n_workers=n_workers,
      seed=seed
    )

    self.n_requests = 0

  def request(self, *args):
    if self.processes is None:
      raise ValueError('Mill has already been stopped!')

    self.n_requests += 1
    self.command_queue.put(args)


  def retrieve(self):
    if self.processes is None:
      raise ValueError('Mill has already been stopped!')

    if self.n_requests <= 0:
      raise ValueError('Attempt to retrieve without request! Consider calling `request` method first.')

    try:
      args, batch = self.queue.get(block=True)
      self.queue.task_done()

      self.n_requests -= 1

      return args, batch
    except:
      import warnings
      warnings.warn('An exception occurred while retrieving. Cleaning queue.')
      while not self.queue.empty():
        self.queue.get()
        self.queue.task_done()

      raise ...

PythiaMill = CachedPythiaMill

