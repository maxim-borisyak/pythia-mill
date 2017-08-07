from pythiamill.utils import launch_pythia, SDetector

import numpy as np

detector = SDetector(10, R = 100.0)

buffer = launch_pythia([
  'Init:showProcesses = off',
  'Init:showMultipartonInteractions = off',
  'Init:showChangedSettings = off',
  'Init:showChangedParticleData = off',
  'Stat:showPartonLevel = off',
  "Beams:eCM = 14000",
  "HardQCD:all = on",
  "PhaseSpace:pTHatMin = 20.",
], detector, n_samples=1024 * 4)

import matplotlib.pyplot as plt
plt.figure(figsize=(8, 8))
buffer = np.asarray(buffer)
ind = np.where(buffer > 0.0, 1.0, 0.0)

plt.imshow(np.mean(ind, axis=0).T, interpolation='None', cmap=plt.cm.plasma, origin='lower', extent=[-10, 10, -3.14, 3.14])
plt.xlabel('Pseudorapidity')
plt.ylabel(r'$\phi$')
plt.colorbar()
plt.show()