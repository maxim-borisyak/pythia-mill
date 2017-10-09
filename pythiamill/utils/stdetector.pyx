cimport cython
import cython
from pythiautils cimport Pythia, Event, Sphericity, Thrust, FLOAT
from stdetector cimport STDetector

ctypedef cnp.uint8_t uint8

cdef class STDetector(Detector):
  def __init__(self):
    self.sph = Sphericity(2.0, 2)
    self.lin = Sphericity(1.0, 2)
    self.thr = Thrust(2)

  @cython.boundscheck(False)
  @cython.nonecheck(False)
  @cython.overflowcheck(False)
  @cython.wraparound(False)
  @cython.infer_types(True)
  cpdef void view(self, FLOAT[:] buffer):
    cdef Pythia * pythia = self.pythia

    with nogil:
      self.sph.analyze(pythia.event)
      buffer[0] = self.sph.sphericity()

      self.lin.analyze(pythia.event)
      buffer[1] = self.lin.sphericity()

      self.thr.analyze(pythia.event)
      buffer[2] = self.thr.thrust()
