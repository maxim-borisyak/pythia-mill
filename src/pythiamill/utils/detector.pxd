cimport cython
import cython
from .pythiautils cimport Pythia, FLOAT


cdef class Detector:
  cdef Pythia * pythia
  cdef bind(self, Pythia * pythia)

  cpdef void view(self, FLOAT[:] buffer, tuple args)