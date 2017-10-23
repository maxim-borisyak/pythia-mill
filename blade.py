import numpy as np

from pythiamill.utils import *

import sys

default_options = [
  'Print:quiet = on',
  'Init:showProcesses = off',
  'Init:showMultipartonInteractions = off',
  'Init:showChangedSettings = off',
  'Init:showChangedParticleData = off',
]

def blade():
  output_path = sys.argv[1]
  n_samples = int(sys.argv[2])
  detector_class = sys.argv[3]

  if detector_class == 'SDetector':
    w, h = int(sys.argv[4]), int(sys.argv[5])
    pythia_options = sys.argv[6:]
    detector = SDetector(w, h)()
  elif detector_class == 'STDetector':
    detector = STDetector()()
    pythia_options = sys.argv[4:]
  else:
    raise ValueError('Unknown detector!')

  print('Launching pythia with the following options:\n%s' % '\n'.join(default_options + pythia_options))

  pythia = launch_pythia(default_options + pythia_options)
  buffer = np.ndarray(shape=(n_samples, detector.event_size()), dtype='float32')
  pythia_worker(detector, pythia, buffer)

  np.save(output_path, buffer)

if __name__ == '__main__':
  try:
    blade()
  except Exception as e:
    print(
      """
      Error [%s] occurred during call [%s].
      Usage:
      python blade.py <output path> <number of events to generate> SDetector <number of cells by pseudo-rapidity> <number of cells by phi> <pythia options>
        or
      python blade.py <output path> <number of events to generate> STDetector <pythia options>  
      """ % (e, ' '.join(sys.argv))
    )