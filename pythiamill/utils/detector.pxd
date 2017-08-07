cimport numpy as cnp

from pythiautils cimport Pythia, FLOAT

cdef class Detector:
  cdef void view(self, Pythia * pythia, FLOAT[:, :] buffer) nogil