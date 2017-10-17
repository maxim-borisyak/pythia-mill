from libcpp cimport bool

cdef extern from '<string>' namespace 'std' nogil:
  cdef cppclass string:
    string(char *) except +

ctypedef string cppstring

cdef extern from "Pythia8/Event.h" namespace "Pythia8" nogil:
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

cdef extern from "Pythia8/Pythia.h" namespace "Pythia8" nogil:
  cdef cppclass Pythia:
    Pythia() nogil
    bool readString(cppstring, bool warn = true) nogil
    bool init() nogil
    bool next() nogil
    void stat() nogil
    Event event

cdef extern from "Pythia8/Analysis.h" namespace "Pythia8" nogil:
  cdef cppclass Sphericity:
    Sphericity() nogil
    Sphericity(double powerIn, int selectIn) nogil
    bool analyze(const Event& event) nogil
    double sphericity() nogil

  cdef cppclass Thrust:
    Thrust() nogil
    Thrust(int selectIn) nogil
    bool analyze(const Event& event) nogil
    double thrust() nogil

cimport numpy as cnp
ctypedef cnp.float32_t FLOAT