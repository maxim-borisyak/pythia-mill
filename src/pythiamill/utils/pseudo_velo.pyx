cimport cython
import cython
from pythiautils cimport Pythia, Event, FLOAT, float64
from detector cimport Detector

cimport numpy as cnp
import numpy as np

from libc.math cimport sqrt, atanh, tanh, atan2, M_PI, floor
from libc.stdlib cimport rand, srand, RAND_MAX

cdef inline double abs(double x):
  if x > 0.0:
    return x
  else:
    return -x

class PseudoVELOWrapper(object):
  """
  For pickle.
  """
  def __init__(self, n_layers, matrix_size, pixel_size, layer_gap):
    self.args = (n_layers, matrix_size, pixel_size, layer_gap)

  def __call__(self):
    return PseudoVELO(*self.args)

  def event_size(self,):
    return self.args[0] * self.args[1] * self.args[1]

cdef class PseudoVELO(Detector):
  def __init__(self, int n_layers, int matrix_size, float64 pixel_size, float64 layer_gap):
    self.n_layers = n_layers
    self.matrix_size = matrix_size
    self.pixel_size = pixel_size
    self.layer_gap_distance = layer_gap

  def event_size(self):
    return self.n_layers * self.matrix_size * self.matrix_size

  @cython.boundscheck(False)
  @cython.overflowcheck(False)
  @cython.wraparound(False)
  @cython.infer_types(True)
  cpdef void view(self, FLOAT[:] buffer, tuple args):
    cdef Pythia * pythia = self.pythia

    cdef float64 offset
    if args is None:
      offset = -self.n_layers * self.layer_gap_distance / 2.0
    else:
      offset = args[0]

    cdef double matrix_half_size = self.matrix_size * self.pixel_size / 2.0

     ### momentum
    cdef double px, py, pz, p

    ### origin coordinates
    cdef double ox, oy, oz

    ### decay (end) coordinates
    cdef double dx, dy, dz

    ### intersection coordinates
    cdef double ix, iy

    ### pixel indices
    cdef int jx, jy

    cdef double z_to_layer_plane
    cdef double layer_z
    cdef double alpha

    cdef int i, j, k

    for i in range(buffer.shape[0]):
      buffer[i] = 0.0

    for i in range(pythia.event.size()):
      for j in range(self.n_layers):

        px = pythia.event.at(i).px()
        py = pythia.event.at(i).py()
        pz = pythia.event.at(i).pz()

        if abs(pz) < 1.0e-12:
          continue

        p = px * px + py * py + pz * pz

        if p < 1.0e-12:
          ### I guess, nobody would miss such particles
          continue

        ox = pythia.event.at(i).xProd()
        oy = pythia.event.at(i).yProd()
        oz = pythia.event.at(i).zProd()

        dx = pythia.event.at(i).xDec()
        dy = pythia.event.at(i).yDec()
        dz = pythia.event.at(i).zDec()

        layer_z = j * self.layer_gap_distance + offset

        if (oz < 0 and dz < 0) or (oz > 0 and dz > 0):
          continue

        alpha = (layer_z - oz) / pz

        ix = alpha * px + ox
        iy = alpha * py + oy

        ### translate to the matrix origin
        ix += matrix_half_size
        iy += matrix_half_size

        jx = <int> floor(ix / self.pixel_size)
        jy = <int> floor(iy / self.pixel_size)

        if jx >= 0 and jy >= 0 and jy < self.matrix_size and jx < self.matrix_size:
          k = j * self.matrix_size * self.matrix_size + jx * self.matrix_size + jy
          buffer[k] = 1.0













