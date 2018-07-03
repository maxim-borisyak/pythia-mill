import matplotlib.pyplot as plt

def test_cached_mill():
  from pythiamill import PythiaMill
  from pythiamill.utils import SphericalTracker
  from .common import test_pythia_options

  detector = SphericalTracker(is_binary=False)
  mill = PythiaMill(detector, test_pythia_options, cache_size=32, n_workers=4, seed=123)

  for i in range(100):
    sample = mill.sample()

  mill.terminate()

def test_parametrized_mill():
  from pythiamill import ParametrizedPythiaMill
  from pythiamill.utils import SphericalTracker
  from .common import test_pythia_options

  detector = SphericalTracker(is_binary=False)
  mill = ParametrizedPythiaMill(detector, test_pythia_options, n_workers=4, seed=123)

  for i in range(10):
    mill.request(i / 10.0)

  for i in range(10):
    args, sample = mill.retrieve()

  mill.terminate()