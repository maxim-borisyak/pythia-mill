cimport cython
import cython
from .pythiautils cimport Pythia, Event, FLOAT
from .detector cimport Detector

cimport numpy as cnp
import numpy as np

from libc.math cimport sqrt, atanh, tanh, atan2, M_PI, floor
from libc.stdlib cimport rand, srand, RAND_MAX

cdef inline double abs(double x) nogil:
  return -x if x < 0 else x

cdef inline double uniform() nogil:
  return (<double>rand()) / RAND_MAX

cdef inline double intersection_scale(
        double o, double ox, double oy, double oz,
        double p, double px, double py, double pz,
        double R_sqr
) nogil:
  """
  Solves
    (ox + scale * px) ** 2 + (oy + scale * py) ** 2 + (oz + scale * pz) ** 2 = R ** 2
  for scale.
  """
  cdef double d
  cdef double scalar_prod

  scalar_prod = px * ox + py * oy + pz * oz

  d = 4 * scalar_prod * scalar_prod +  4 * p * (R_sqr - o)
  if d < 0.0:
    return -1.0
  else:
    return (1 / p) * (0.5 * sqrt(d) - scalar_prod)

ctypedef cnp.uint8_t uint8

class SphericalTrackerWrapper(object):
  """
  For pickle.
  """
  def __init__(self, is_binary=True,
               pseudorapidity_steps=32, phi_steps=32, n_layers=1, max_pseudorapidity=5, R_min=1.0, R_max = 100.0,
               energy_threshold=0.0):
    self.args = (
      (1 if is_binary else 0),
      pseudorapidity_steps, phi_steps,
      n_layers,
      max_pseudorapidity,
      R_min, R_max,
      energy_threshold,
    )

  def __call__(self):
    return SphericalTracker(*self.args)

  def event_size(self,):
    return self.args[1] * self.args[2] * self.args[3]

cdef class SphericalTracker(Detector):
  def __init__(self, int is_binary, int pseudorapidity_steps, int phi_steps, int n_layers,
               double max_pseudorapidity=5, double R_min=1.0, double R_max=100.0, double energy_threshold=0.0):
    self.pr_steps = pseudorapidity_steps
    self.phi_steps = phi_steps
    self.n_layers = n_layers
    self.R_min = R_min
    self.R_max = R_max

    self.energy_threshold = energy_threshold

    self.is_binary = is_binary

    self.layers_R = np.linspace(R_min, R_max, num=self.n_layers, dtype='float64')
    self.layers_Rsqr = np.ndarray(shape=(self.n_layers, ), dtype='float64')
    cdef int i
    for i in range(self.n_layers):
      self.layers_Rsqr[i] = self.layers_R[i] * self.layers_R[i]

    self.max_pseudorapidity = max_pseudorapidity

  def event_size(self):
    return self.n_layers * self.pr_steps * self.phi_steps

  @cython.boundscheck(False)
  @cython.overflowcheck(False)
  @cython.wraparound(False)
  @cython.infer_types(True)
  cpdef void view(self, FLOAT[:] buffer, tuple args):
    cdef double offset = 0.0
    if len(args) > 0:
      offset = args[0]


    cdef Pythia * pythia = self.pythia

    ### ...
    cdef double max_pseudorapidity = self.max_pseudorapidity

    ### utility constant.
    cdef double max_tanh = tanh(max_pseudorapidity)

    ### number of steps in pseudorapidity axis
    cdef int pr_steps = self.pr_steps
    ### size of one pseudorapidity step
    cdef double pr_step = 2 * max_pseudorapidity / pr_steps

    ### the same for phi
    cdef int phi_steps = self.phi_steps
    cdef double phi_step = 2 * M_PI / phi_steps

    ### momentum
    cdef double px, py, pz

    ### origin coordinates
    cdef double ox, oy, oz

    ### decay (end) coordinates
    cdef double dx, dy, dz

    ### utility deltas
    cdef double ax, ay, az

    ### coordinates of intersection with the detector sphere
    cdef double ix, iy, iz

    ### pseudorapidity
    cdef double pr
    cdef double phi

    ### norm of the origin vector, squared
    cdef double o

    ### norm of the decay vector, squared
    cdef double d

    ### norm of the momentum vector, squared
    cdef double p

    ### norm of the delta vector, squared
    cdef double a

    ### squared radius of the current VELO layer
    cdef double R_sqr, R

    ### || o + scale * p || = R
    cdef double scale

    ### tanh of pseudorapidity
    ### pr = atanh(iz / R), thus th = iz / R
    cdef double th

    ### position of the cells in the grid
    cdef int pr_i, phi_i

    cdef int i, j
    cdef int indx

    buffer[:] = 0.0

    for i in range(pythia.event.size()):
      for j in range(self.n_layers):
        R_sqr = self.layers_Rsqr[j]
        R = self.layers_R[j]

        px = pythia.event.at(i).px()
        py = pythia.event.at(i).py()
        pz = pythia.event.at(i).pz()

        p = px * px + py * py + pz * pz

        if p < 1.0e-12:
          ### I guess, nobody would miss such particles
          continue

        ox = pythia.event.at(i).xProd()
        oy = pythia.event.at(i).yProd()
        oz = pythia.event.at(i).zProd() + offset

        dx = pythia.event.at(i).xDec()
        dy = pythia.event.at(i).yDec()
        dz = pythia.event.at(i).zDec() + offset

        ax = dx - ox
        ay = dy - oy
        az = dz - oz
        a = ax * ax + ay * ay + az * az

        if (a < 1.0e-9):
          ### particle decayed immediately
          continue

        o = ox * ox + oy * oy + oz * oz
        d = dx * dx + dy * dy + dz * dz

        if (o >= R_sqr and d >= R_sqr) or (o <= R_sqr and d <= R_sqr):
          ### the particle originates and decays
          ### either outside or inside the detector
          continue

        ### solution of ||origin + scale * (decay - origin)|| = R for scale
        scale = intersection_scale(o, ox, oy, oz, a, ax, ay, az, R_sqr)

        if scale < 0.0 or scale > 1.0:
          ### this should not happen
          continue

        ### coordinates of intersection
        ix = ox + scale * ax
        iy = oy + scale * ay
        iz = oz + scale * az

        ### ix ** 2 + iy ** 2 + iz ** 2 must sum to R ** 2
        th = abs(iz) / R

        ### to avoid expensive atanh call
        ### Note: tanh and atanh are monotonous.
        if th >= max_tanh:
          ### particle too close to the beam axis
          continue

        ### actual pseudorapidity (abs of it)
        pr = atanh(th)
        pr_i = <int> floor(pr / pr_step)

        ### the negative semi-sphere.
        if iz < 0:
          pr_i = -pr_i - 1

        pr_i += pr_steps / 2

        ### phi is just atan, pi shift is just to compensate for negative angels
        phi = atan2(iy, ix) + M_PI
        phi_i = <int> floor(phi / phi_step)

        ### tracker activation
        if pythia.event.at(i).isCharged():
          indx = j * (phi_steps * pr_steps) + pr_i * phi_steps + phi_i

          if self.is_binary:
            if pythia.event.at(i).e() > self.energy_threshold:
              buffer[indx] = 1.0
          else:
            buffer[indx] += pythia.event.at(i).e()
