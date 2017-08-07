from libcpp cimport bool
from libcpp.string cimport string as cstring

cdef extern from "Pythia8/Event.h" namespace "Pythia8":
  cdef cppclass Particle:
    int    id()        nogil
    int    status()    nogil
    int    mother1()   nogil
    int    mother2()   nogil
    int    daughter1() nogil
    int    daughter2() nogil
    int    col()       nogil
    int    acol()      nogil
    double px()        nogil
    double py()        nogil
    double pz()        nogil
    double e()         nogil
    double m()         nogil
    double scale()     nogil
    double pol()       nogil
    bool   hasVertex() nogil
    double xProd()     nogil
    double yProd()     nogil
    double zProd()     nogil
    double tProd()     nogil
    double tau()       nogil

    int    idAbs()     nogil
    int    statusAbs() nogil
    bool   isFinal()   nogil
    int    intPol()    nogil

    bool isCharged() nogil

  cdef cppclass Event:
    Particle& front() nogil
    Particle& at(int i) nogil
    Particle& back() nogil

    int size() nogil;

cdef extern from "Pythia8/Pythia.h" namespace "Pythia8":
  cdef cppclass Pythia:
    Pythia() nogil
    bool readString(cstring, bool warn = true) nogil
    bool init() nogil
    bool next() nogil
    void stat() nogil
    Event event;

cimport numpy as cnp
ctypedef cnp.float32_t FLOAT