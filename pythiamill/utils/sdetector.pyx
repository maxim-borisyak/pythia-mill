cimport cython
import cython
from detector cimport Detector, FLOAT
from pythiautils cimport Pythia, Event

from libc.math cimport sqrt, atanh, tanh, atan2, M_PI, floor

cdef inline double abs(double x) nogil:
  return -x if x < 0 else x

cdef inline double intersection_scale(
        double o, double ox, double oy, double oz,
        double p, double px, double py, double pz,
        double R_sqr
) nogil:
  cdef double d
  cdef double scalar_prod

  scalar_prod = px * ox + py * oy + pz * oz

  ### solution of
  ### (ox + scale * px) ** 2 + (oy + scale * py) ** 2 + (oz + scale * pz) ** 2 = R ** 2
  ### for scale
  d = 4 * scalar_prod * scalar_prod +  4 * p * (R_sqr - o)

  return (1 / p) * (0.5 * sqrt(d) - scalar_prod)

@cython.boundscheck(False)
@cython.nonecheck(False)
@cython.overflowcheck(False)
@cython.wraparound(False)
@cython.infer_types(True)
cdef class SDetector(Detector):
  """
  Yeeeh... You need to go this far to simply implement partial application...
  """
  cdef double max_pseudorapidity
  cdef double max_tanh
  cdef double R

  def __init__(self, double max_pseudorapidity, double R = 1.0):
    self.max_pseudorapidity = max_pseudorapidity
    self.max_tanh = tanh(max_pseudorapidity)
    self.R = R

  cdef void view(self, Pythia * pythia, FLOAT[:, :] buffer) nogil:
    cdef int pr_steps = buffer.shape[0]
    cdef double pr_step = 2 * self.max_pseudorapidity / pr_steps

    cdef int phi_cells = buffer.shape[1]
    cdef double phi_step = 2 * M_PI / phi_cells

    cdef double px, py, pz
    cdef double ox, oy, oz
    cdef double ix, iy, iz

    cdef double pr
    cdef double phi
    cdef double o
    cdef double p
    cdef double R_sqr = self.R * self.R
    cdef double scale
    cdef double th

    cdef int pr_i, phi_i

    cdef int i

    buffer[:, :] = 0.0

    for i in range(pythia.event.size()):
      if pythia.event.at(i).isCharged() and pythia.event.at(i).isFinal():
        px = pythia.event.at(i).px()
        py = pythia.event.at(i).py()
        pz = pythia.event.at(i).pz()

        p = px * px + py * py + pz * pz

        if p < 1.0e-12:
          ### I guess, nobody would miss such particles
          continue

        ox = pythia.event.at(i).xProd()
        oy = pythia.event.at(i).yProd()
        oz = pythia.event.at(i).zProd()

        o = ox * ox + oy * oy + oz * oz
        if o > R_sqr:
          ### Particle originates outside the detector
          ### could in principle return back,
          ### but ignoring for now.
          continue

        ### solution of ||o + scale * p|| = R for scale
        ### for positive scale
        scale = intersection_scale(o, ox, oy, oz, p, px, py, pz, R_sqr)

        ix = ox + scale * px
        iy = oy + scale * py
        iz = oz + scale * pz

        ### ix ** 2 + iy ** 2 + iz ** 2 must sum to R ** 2
        th = abs(iz) / self.R

        ### to avoid expensive atanh call
        ### Note: tanh and atanh are monotonous.
        if th >= self.max_tanh:
          continue

        pr = atanh(th)
        pr_i = <int> floor(pr / pr_step)

        ### the negative semi-sphere.
        if iz < 0:
          pr_i = -pr_i - 1

        pr_i += pr_steps / 2

        phi = atan2(iy, ix) + M_PI
        phi_i = <int> floor(phi / phi_step)

        buffer[pr_i, phi_i] += pythia.event.at(i).e()

    return