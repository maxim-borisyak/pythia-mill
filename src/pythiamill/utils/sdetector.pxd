cimport numpy as cnp

from .pythiautils cimport Pythia, FLOAT
from .detector cimport Detector

cdef class SDetector(Detector):
  cdef int pr_steps
  cdef int phi_steps

  cdef double max_pseudorapidity
  cdef double R
  cdef double tracker_threshold

  cpdef void view(self, FLOAT[:] buffer, tuple args)