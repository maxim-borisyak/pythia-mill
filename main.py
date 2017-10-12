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

detector = STDetector()

buffer = np.ndarray(shape=(8, 3), dtype='float32')

pythia = launch_pythia(options)

#pythia_worker(detector, pythia, buffer)

start = time()
pythia_worker(detector, pythia, buffer)
end = time()

print 'Time %.3lf millisec' % ((end - start) * 1000.0)
