# cython: profile=True
# cython: linetrace=True

cimport numpy as cnp

from pythiautils cimport Pythia, FLOAT
from detector cimport Detector

cdef class TuneMCDetector(Detector):
  cpdef void view(self, FLOAT[:] buffer)

cdef extern from "TuneMC.h" nogil:
  void tune_mc_features(Pythia * pythia, float * buffer) nogil
