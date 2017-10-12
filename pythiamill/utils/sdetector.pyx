cimport cython
import cython
from pythiautils cimport Pythia, Event, FLOAT
from detector cimport Detector

from libc.math cimport sqrt, atanh, tanh, atan2, M_PI, floor

DEF tracker_channel = 0
DEF rich_channel = 1
DEF calo_channel = 2

DEF electron = 11
DEF muon = 13
DEF pi_plus = 211
DEF K_0 = 321
DEF proton = 2212
DEF photon = 22

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

ctypedef cnp.uint8_t uint8

cdef class SDetector(Detector):
  def __init__(self, int pseudorapidity_steps, int phi_steps,
               double max_pseudorapidity = 5, double R = 100.0, double tracker_threshold=0.0):
    self.pr_steps = pseudorapidity_steps
    self.phi_steps = phi_steps

    self.max_pseudorapidity = max_pseudorapidity
    self.R = R
    self.tracker_threshold = tracker_threshold

  def event_size(self):
    return 3 * self.pr_steps * self.phi_steps

  @cython.boundscheck(False)
  @cython.nonecheck(False)
  @cython.overflowcheck(False)
  @cython.wraparound(False)
  @cython.infer_types(True)
  cpdef void view(self, FLOAT[:] buffer):
    cdef Pythia * pythia = self.pythia

    ### ...
    cdef double max_pseudorapidity = self.max_pseudorapidity

    ### minimal energy required to activate tracker
    cdef double tracker_threshold = self.tracker_threshold
    ### detector raduis
    cdef double R = self.R

    ### utility constant.
    cdef double max_tanh = tanh(max_pseudorapidity)

    ### number of steps in pseudorapidity axis
    cdef int pr_steps = self.pr_steps
    ### size of one pseudorapidity step
    cdef double pr_step = 2 * max_pseudorapidity / pr_steps

    ### the same for phi
    cdef int phi_cells = self.phi_steps
    cdef double phi_step = 2 * M_PI / phi_cells

    ### momentum
    cdef double px, py, pz

    ### origin coordinates
    cdef double ox, oy, oz

    ### coordinates of intersection with the detector sphere
    cdef double ix, iy, iz

    ### pseudorapidity
    cdef double pr
    cdef double phi

    ### norm of the origin vector, squared
    cdef double o
    ### norm of the momentum vector, squared
    cdef double p
    cdef double R_sqr = R * R

    ### || o + scale * p || = R
    cdef double scale

    ### tanh of pseudorapidity
    ### pr = atanh(iz / R), thus th = iz / R
    cdef double th

    ### position of the cells in the grid
    cdef int pr_i, phi_i

    cdef int i
    cdef int indx

    with nogil:
      buffer[:] = 0.0

      for i in range(pythia.event.size()):
        if not pythia.event.at(i).isFinal():
          continue

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

        ### coordinates of intersection
        ix = ox + scale * px
        iy = oy + scale * py
        iz = oz + scale * pz

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
        if pythia.event.at(i).e() > tracker_threshold:
          indx = pr_i * self.phi_steps + phi_i
          buffer[indx] = 1.0

        ### rich reacts on all charged particles (why is it so?)
        if pythia.event.at(i).isCharged():
          indx = self.phi_steps * self.pr_steps + pr_i * self.phi_steps + phi_i
          buffer[indx] += pythia.event.at(i).e()

        ### calo react on all charged particles except muons or on photons
        if (pythia.event.at(i).isCharged() and pythia.event.at(i).idAbs() != muon) or pythia.event.at(i).idAbs() == photon:
          indx = 2 * self.phi_steps * self.pr_steps + pr_i * self.phi_steps + phi_i
          buffer[indx] += pythia.event.at(i).e()