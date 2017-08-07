from pythiautils cimport Pythia, Particle, FLOAT
from detector cimport Detector
from libcpp.string cimport string as cstring

import time
import cython
cimport cython

import numpy as np
cimport numpy as cnp

from cpython.string cimport PyString_AsString

from libc.stdlib cimport malloc, free

stuff = 'hi!'

def launch_pythia(list options, Detector detector, int n_samples):
  cdef int opt_len = len(options)
  cdef char ** c_options = <char **>malloc(opt_len * sizeof(char*))
  cdef FLOAT[:, :, :] buffer = np.ndarray(shape=(n_samples, 256, 64), dtype=np.float32)

  for i in range(opt_len):
    c_options[i] = PyString_AsString(options[i])

  with nogil:
    pythia_worker(opt_len, c_options, detector, buffer)
    free(c_options)

  return buffer

@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef void pythia_worker(
  int n_options, char ** options,
  Detector detector,
  FLOAT[:, :, :] buffer,
) nogil:

  cdef Pythia pythia
  cdef Pythia * pythia_prt = &pythia

  cdef int i, j

  for i in range(n_options):
    pythia.readString(cstring(options[i]))
  pythia.init()

  cdef int nCharged = 0

  for i in range(buffer.shape[0]):
    if not pythia.next():
      continue

    detector.view(pythia_prt, buffer[i])