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
  'Beams:idA =  11',
  "Beams:idB = -11",
  "Beams:eCM = 91.188",
  '23:onMode = off',
  '23:onIfAny = 1 2 3 4 5',
  'WeakSingleBoson:ffbar2gmZ = on',
  'PDF:lepton = off',
  'StringFlav:thetaPS = 40.4',
  'StringFlav:thetaV = 3.32',
  'StringZ:usePetersonC=off',
  'StringZ:usePetersonB=off',
  'StringZ:usePetersonH=off',
  'ParticleDecays:multIncrease=4.5',
  'ParticleDecays:multIncreaseWeak=2.0',
  'ParticleDecays:FSRinDecays=on',
  'TimeShower:QEDshowerByQ=on'
]

if __name__ == '__main__':

  buffer = np.ndarray(shape=(8, 3), dtype='float32')

  mill = PythiaMill(STDetector(), options, cache_size=16, batch_size=16)

  #pythia_worker(detector, pythia, buffer)

  start = time()
  mill.sample()
  end = time()

  mill.terminate()

  print('Time %.3lf millisec' % ((end - start) * 1000.0))
