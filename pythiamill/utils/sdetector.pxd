cimport numpy as cnp

from pythiautils cimport Pythia, FLOAT
from detector cimport Detector

cdef class SDetector(Detector):
  cdef int pr_steps;
  cdef int phi_steps;

  cpdef void view(self, FLOAT[:] buffer_)