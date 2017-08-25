cimport numpy as cnp

from pythiautils cimport Pythia, FLOAT

cdef void view(Pythia * pythia, FLOAT[:, :, :] buffer) nogil