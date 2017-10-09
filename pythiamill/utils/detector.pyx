cimport cython
import cython
from pythiautils cimport Pythia, FLOAT
from detector cimport Detector


cdef class Detector:
  cdef bind(self, Pythia * pythia):
    self.pythia = pythia

  cpdef void view(self, FLOAT[:] buffer):
    pass