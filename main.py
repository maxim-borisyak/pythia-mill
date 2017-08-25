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

mill = PythiaMill(options, batch_size=1, cache_size=128, buffer_size=1024)

from time import time
start_time = time()

mill.wait_unit(128)

end_time = time()

delta = (end_time - start_time) * 1000.0

print '%.3f millisec per event' % (delta / 1024)

mill.terminate()