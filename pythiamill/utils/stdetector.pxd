# cython: profile=True

cimport numpy as cnp

from pythiautils cimport Pythia, FLOAT, Sphericity, Thrust
from detector cimport Detector

cdef class STDetector(Detector):
  cdef Sphericity sph
  cdef Sphericity lin
  cdef Thrust thr

  cpdef void view(self, FLOAT[:] buffer)