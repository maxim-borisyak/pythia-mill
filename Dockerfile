FROM python:3

### rsync for make install
RUN apt-get update
RUN apt-get install -y rsync

### additional flags to pass to gcc for Pythia compilation
ENV PYTHIA_ADDITIONAL_FLAGS -msse4.2 -mavx

ENV PYTHIA_LIB /usr/opt/pythia/lib
ENV PYTHIA_INCLUDE /usr/opt/pythia/include

ENV LD_LIBRARY_PATH "$LD_LIBRARY_PATH:$PYTHIA_LIB"
ENV INCLUDE_PATH "$INCLUDE_PATH:$PYTHIA_INCLUDE"

WORKDIR /usr/opt

### download pythia
ADD http://home.thep.lu.se/~torbjorn/pythia8/pythia8230.tgz /usr/opt/pythia8230.tgz

RUN tar xvfz pythia8230.tgz

WORKDIR /usr/opt/pythia8230

### compilation
RUN ./configure --cxx-common="-Ofast -O3 -fPIC $PYTHIA_ADDITIONAL_FLAGS" --cxx-shared="-Ofast -O3 -fPIC -shared $PYTHIA_ADDITIONAL_FLAGS" --prefix=/usr/opt/pythia --enable-64bit --enable-shared
RUN make -j4
RUN make install

### the only python dependencies
### should be installed beforehand
RUN pip install numpy cython

WORKDIR /usr/app

COPY . /usr/app/

### compiling all cython extensions
RUN python setup.py build_ext --inplace

ENTRYPOINT ["python", "blade.py"]

CMD ["events.npy", "32", "SDetector", "32", "32", "Beams:idA =  11", "Beams:idB = -11", "Beams:eCM = 91.188", "23:onMode = off", "23:onIfAny = 1 2 3 4 5", "WeakSingleBoson:ffbar2gmZ = on", "StringZ:usePetersonC=off", "StringZ:usePetersonB=off", "StringZ:usePetersonH=off", "ParticleDecays:FSRinDecays=on", "TimeShower:QEDshowerByQ=on"]