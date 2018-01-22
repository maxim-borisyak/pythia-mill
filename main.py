from pythiamill import PythiaMill
from pythiamill.utils import *
from time import time

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
  'TimeShower:QEDshowerByQ=on',
  'Random:seed=0'
]

if __name__ == '__main__':
  n_batches = 100
  batch_size = 1024
  n_workers = 4

  mill = PythiaMill(TuneMCDetector(), options, cache_size=16, batch_size=batch_size, n_workers=n_workers)

  start = time()
  for i in range(n_batches):
    a = mill.sample()
  end = time()

  delta = end - start
  mill.terminate()
  print('Total wall time: %.3lf sec' % delta)
  print('Per batch: %.3lf millisec' % (delta / n_batches * n_workers * 1000))
  print('Per sample: %.3lf millisec' % (delta / n_batches / batch_size * n_workers * 1000))
