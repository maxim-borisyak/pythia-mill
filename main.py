from pythiamill import PythiaMill

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

mill = PythiaMill(options, n_workers=4, batch_size=32, cache_size=1024)

from time import time
start_time = time()

for _ in range(2 ** 10 / 32):
  mill.sample()

end_time = time()

delta = (end_time - start_time) * 1000.0

print '%.3f millisec per event' % (delta / 1024)

mill.terminate()