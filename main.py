import numpy as np
from pythiamill import PythiaMill

from pythiamill.utils import *

from time import time
import cProfile, pstats

options=[
  'Print:quiet = on',
  'Init:showProcesses = off',
  'Init:showMultipartonInteractions = off',
  'Init:showChangedSettings = off',
  'Init:showChangedParticleData = off',
  'Stat:showPartonLevel = off',
  "Beams:eCM = 18000",
  "HardQCD:all = on",
  "PhaseSpace:pTHatMin = 20.",
]

if __name__ == '__main__':

  buffer = np.ndarray(shape=(8, 3), dtype='float32')

  mill = PythiaMill(STDetector(), options, cache_size=16)

  #pythia_worker(detector, pythia, buffer)

  start = time()
  mill.sample()
  end = time()

  mill.terminate()

  print('Time %.3lf millisec' % ((end - start) * 1000.0))
