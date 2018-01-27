cimport numpy as cnp

from pythiautils cimport Pythia, float32, float64, FLOAT
from detector cimport Detector

cdef class SVELO(Detector):
  cdef int pr_steps
  cdef int phi_steps
  cdef int n_layers

  cdef float64 R_min, R_max
  cdef float64[:] layers_R
  cdef float64[:] layers_Rsqr

  cdef float64 max_pseudorapidity
  cdef float64 energy_threshold
  cdef float64 activation_probability

  cpdef void view(self, FLOAT[:] buffer_)
