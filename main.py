from pythiamill import PythiaMill

from pythiamill.utils.stdetector import STDetector

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

mill = PythiaMill(detector, options, event_size=4, n_workers=4, batch_size=32, cache_size=32)

X = mill.sample()

mill.terminate()

print X.shape

print X[:10, :]

