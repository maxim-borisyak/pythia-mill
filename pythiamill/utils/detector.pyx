cimport numpy as cnp

from detector cimport Detector
from pythiautils cimport Pythia, FLOAT

cdef class Detector:
  cdef void view(self, Pythia * pythia, FLOAT[:, :] buffer) nogil:
    pass