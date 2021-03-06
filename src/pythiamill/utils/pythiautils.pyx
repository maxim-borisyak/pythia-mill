from .pythiautils cimport Pythia, Particle, FLOAT, cppstring
from .detector cimport Detector

import cython
cimport cython

#from cpython.string cimport PyBytes_AsString

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

cdef char * _chars(s):
  cdef char * str
  cdef int i

  if isinstance(s, unicode):
    # encode to the specific encoding used inside of the module
    s = (<unicode>s).encode('utf8')

  str = <char *>malloc((len(s) + 1) * sizeof(char))

  for i in range(len(s)):
    str[i] = s[i]

  str[len(s)] = '\0'
  return str

@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void configure_pythia(PyPythia pypythia, list options):
  cdef int opt_len = len(options)
  cdef char ** c_options = <char **> malloc(opt_len * sizeof(char*))
  cdef char * c_str
  cdef int i, j

  for i in range(opt_len):
    c_str = _chars(options[i])
    c_options[i] = c_str

  for i in range(opt_len):
    pypythia.get_pythia().readString(cppstring(c_options[i]))
  pypythia.get_pythia().init()

  for i in range(opt_len):
    free(c_options[i])

  free(c_options)

@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef PyPythia launch_pythia(list options):

  cdef PyPythia pypythia = PyPythia()
  configure_pythia(pypythia, options)

  return pypythia


@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void bind_detector(Detector detector, PyPythia pypythia):
  cdef Pythia * pythia = pypythia.get_pythia()
  detector.bind(pythia)

@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef bool check_pythia(PyPythia pypythia):
  cdef Pythia * pythia = pypythia.get_pythia()
  return not pythia.next()

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void pythia_worker(Detector detector, PyPythia pypythia, FLOAT[:, :] buffer, tuple args):
  cdef Pythia * pythia = pypythia.get_pythia()
  detector.bind(pythia)

  cdef int i = 0
  while i < buffer.shape[0]:
    if not pythia.next():
      continue

    detector.view(buffer[i], args)
    i += 1