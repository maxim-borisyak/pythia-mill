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
RUN ./configure --cxx-common="-Ofast -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++98 -pedantic -W -Wall -Wshadow -fPIC $PYTHIA_ADDITIONAL_FLAGS" --cxx-shared="-Ofast -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++98 -pedantic -W -Wall -Wshadow -fPIC -shared $PYTHIA_ADDITIONAL_FLAGS" --prefix=/usr/opt/pythia --enable-64bit --enable-shared
RUN make -j4
RUN make install

### the only python dependencies
### should be installed beforehand
RUN pip install numpy cython tqdm

WORKDIR /usr/app

COPY . /usr/app/

### compiling all cython extensions
RUN python setup.py build_ext --inplace

ENTRYPOINT ["python", "main.py"]
