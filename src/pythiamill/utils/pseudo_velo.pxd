cimport numpy as cnp

from pythiautils cimport Pythia, float32, float64, FLOAT
from detector cimport Detector

cdef class PseudoVELO(Detector):
  cdef int n_layers
  cdef int matrix_size

  cdef float64 pixel_size
  cdef float64 layer_gap_distance

  cpdef void view(self, FLOAT[:] buffer, tuple args)
