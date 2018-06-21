import multiprocessing as mp

def test_blade():
  from pythiamill import pythia_blade
  from pythiamill.utils import SphericalTracker
  from .common import test_pythia_options

  ctx = mp.get_context('spawn')

  command_queue = ctx.JoinableQueue()
  result_queue = ctx.JoinableQueue()
  detector = SphericalTracker(is_binary=False)

  command_queue.put((1.0, ))
  command_queue.put(None)

  blade = pythia_blade(detector, command_queue, result_queue, options=test_pythia_options, batch_size=32)

  print(result_queue.get(block=True))
  print(result_queue.get(block=True))

def test_blade_process():
  from pythiamill import pythia_blade
  from pythiamill.utils import SphericalTracker
  from .common import test_pythia_options

  ctx = mp.get_context('spawn')

  command_queue = ctx.JoinableQueue()
  result_queue = ctx.JoinableQueue()
  detector = SphericalTracker(is_binary=False)

  p = ctx.Process(
    target=pythia_blade,
    kwargs=dict(
      detector_factory=detector,
      command_queue=command_queue,
      queue=result_queue,
      options=test_pythia_options,
      batch_size=32
    )
  )

  p.start()

  command_queue.put((1.0, ))
  command_queue.put(None)

  print('Is process alive:', p.is_alive())

  print(result_queue.get(block=True))
  print(result_queue.get(block=True))

  p.terminate()

