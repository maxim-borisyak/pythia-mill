import time
import numpy as np

def test_configure():
  import os

  print(os.environ)
  from pythiamill.utils import launch_pythia, configure_pythia
  from .common import test_pythia_options

  get_options = lambda x: test_pythia_options + ["Beams:eCM = %.1lf" % x]

  n = 5

  pythia = launch_pythia(get_options(8000))

  start_time = time.time()

  for _ in range(n):
    configure_pythia(pythia, get_options(np.random.uniform(8000)))

  configure_time = time.time() - start_time

  start_time = time.time()

  for _ in range(n):
    a = get_options(np.random.uniform(8000))

  time_bias = time.time() - start_time

  print('Time: %.3lf milliseconds per iteration' % ( (configure_time - time_bias) / n * 1000 ))
