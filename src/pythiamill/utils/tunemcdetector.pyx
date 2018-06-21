# cython: profile=True
# cython: linetrace=True

cimport cython
import cython
from .pythiautils cimport Pythia, FLOAT
from .tunemcdetector cimport tune_mc_features, TuneMCDetector

ctypedef cnp.uint8_t uint8

class TuneMCDetectorWrapper(object):
  """
  For pickle.
  """
  def __init__(self):
    self.args = tuple()

  def __call__(self):
    return TuneMCDetector(*self.args)

  def event_size(self):
    return (17 + 2) * 2 \
           + (20 + 2) * 2 \
           + (25 + 2) * 2 \
           + (19 + 2) * 4 \
           + (28 + 2) * 2 \
           + (40 + 2) * 2 \
           + (20 + 2) * 2 \
           + 10 + 9 + 9 + 8 \
           + 1

cdef class TuneMCDetector(Detector):
  def __init__(self, *args):
    pass

  def event_size(self):
    return (17 + 2) * 2 \
           + (20 + 2) * 2 \
           + (25 + 2) * 2 \
           + (19 + 2) * 4 \
           + (28 + 2) * 2 \
           + (40 + 2) * 2 \
           + (20 + 2) * 2 \
           + 10 + 9 + 9 + 8 \
           + 1

  @cython.boundscheck(False)
  @cython.overflowcheck(False)
  @cython.wraparound(False)
  @cython.infer_types(True)
  cpdef void view(self, FLOAT[:] buffer, tuple args):
    cdef Pythia * pythia = self.pythia
    cdef float * buffer_ = &(buffer[0])
    tune_mc_features(pythia, buffer_)
