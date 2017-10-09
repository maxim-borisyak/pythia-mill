from pythiautils cimport Pythia, Particle, FLOAT
from detector cimport Detector
from libcpp.string cimport string as cstring

import cython
cimport cython

from cpython.string cimport PyString_AsString

from libc.stdlib cimport malloc, free

ctypedef cnp.uint8_t uint8

cdef class PyPythia:
  cdef Pythia * pythia
  def __cinit__(self):
    self.pythia = new Pythia()

  cdef Pythia * get_pythia(self) nogil:
    return self.pythia

  def __dealloc__(self):
    del self.pythia

@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef PyPythia launch_pythia(list options):
  cdef int opt_len = len(options)
  cdef char ** c_options = <char **> malloc(opt_len * sizeof(char*))

  for i in range(opt_len):
    c_options[i] = PyString_AsString(options[i])

  cdef PyPythia pypythia = PyPythia()

  for i in range(opt_len):
    pypythia.get_pythia().readString(options[i])
  pypythia.get_pythia().init()

  free(c_options)

  return pypythia

@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void pythia_worker(Detector detector, PyPythia pypythia, FLOAT[:, :] buffer):
  cdef Pythia * pythia = pypythia.get_pythia()
  detector.bind(pythia)

  cdef int i = 0
  while i < buffer.shape[0]:
    if not pythia.next():
      continue

    detector.view(buffer[i])
    i += 1