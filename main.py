from pythiamill import PythiaMill
from pythiamill.utils import *
from time import time

import numpy as np

from tqdm import tqdm

options=[
  'Print:quiet = on',
  'Init:showProcesses = off',
  'Init:showMultipartonInteractions = off',
  'Init:showChangedSettings = off',
  'Init:showChangedParticleData = off',
  'Next:numberCount=0',
  'Next:numberShowInfo=0',
  'Next:numberShowEvent=0',
  'Stat:showProcessLevel=off',
  'Stat:showErrors=off',
  'Beams:idA =  2212',
  "Beams:idB = 2212",
  "Beams:eCM = 8000",
  'HardQCD:all = on',
  'PromptPhoton:all = on',
  "PhaseSpace:pTHatMin = 20"
  #'Random:seed=0'
]

if __name__ == '__main__':
  n_batches = 1024
  batch_size = 128
  n_workers = 8

  detector = SVELO(
    pseudorapidity_steps = 32, phi_steps = 32,
    n_layers = 10, R_min=1, R_max = 21,
    activation_probability=0.5
  )
  mill = PythiaMill(detector, options, cache_size=16, batch_size=batch_size, n_workers=n_workers, seed=123)

  start = time()
  data = np.vstack([
    mill.sample().reshape(-1, 10, 32, 32)
    for _ in tqdm(range(n_batches))
  ])
  end = time()
  mill.terminate()

  np.save('events.npy', data)

  delta = end - start
  mill.terminate()
  print('Total wall time: %.3lf sec' % delta)
  print('Per batch: %.3lf millisec' % (delta / n_batches * n_workers * 1000))
  print('Per sample: %.3lf millisec' % (delta / n_batches / batch_size * n_workers * 1000))
