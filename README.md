# pythia-mill
![](http://sr.photos1.fotosearch.com/bthumb/CSP/CSP893/k8938410.jpg)
Small library to launch pythia event generation __in parallel__.


## Pythia8 installation

`PythiaMill` depends on external installation of `Pythia8`.
Pythia8 can be downloaded at [Pythia web site](http://home.thep.lu.se/Pythia/).

In order to get a build compatible with PythiaMill, Pythia8 should be compiled with some specific flags (alternatively, change PythiaMill compile flags in `setup.py`);
The following `configure` options are, most probably, do the trick:

```
./configure --cxx-common='-Ofast -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++98 -pedantic -W -Wall -Wshadow -fPIC' \
  --cxx-shared='-Ofast -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++98 -pedantic -W -Wall -Wshadow -fPIC -shared' \
  --enable-shared --prefix=<place to install pythia>
```

Only two options are different from the default flags: `-Ofast` (`-O2` by default) and `-D_GLIBCXX_USE_CXX11_ABI=0` (absent by default):
- `-Ofast`: Pythia might get measurably faster if compiled with `-03` and `--fast-math` (both are included into `-Ofast`);
- PythiaMill and Pythia must be compiled with the same value of `-D_GLIBCXX_USE_CXX11_ABI`, otherwise, `PythiaMill` might throw errors like the one below:
```
undefined symbol: _ZN7Pythia86Pythia10readStringESsb
```

For example, `pythiamill/utils/pythiautils.so` might contains link (`-D_GLIBCXX_USE_CXX11_ABI=0`):
```
Pythia8::Pythia::readString(std::string, bool)
```

while the signature of the actual function in `Pythia8.so` (`-D_GLIBCXX_USE_CXX11_ABI=1`) might look like:

```
Pythia8::Pythia::readString(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, bool)
```

After configuration step, as usual:
- `make`;
- `make install`.

## PythiaMill installation

`PythiaMill` exploits `cython` as a bridge between `Pythia` and `Python`. Thus, make sure that you have `cython` and `numpy` installed.

There are two options for installation:
- locally (recommended for development):
  ```
  python setup.py build_ext --locally
  ```

  This will just compile `cython` and `C` files.
  To clean all: `python setup.py clean --all`

- as a pip package:
  ```
  pip install git+https://github.com/maxim-borisyak/pythia-mill.git@master
  ```
  or, to quickly update (e.g. to pull some changes):
  ```
  pip install --upgrade --no-deps --force-reinstall git+https://github.com/maxim-borisyak/pythia-mill.git@master
  ```

## Usage

`PythiaMill` launches several worker processes (`PythiaBlade`) and collects their results.

This example pretty much illustrates the basic usage of `PythiaMill`:

```python
from pythiamill import PythiaMill
from pythiamill.utils import *

options=[
  'Beams:eCM = 91.188',
  'Beams:idA =  11',
  'Beams:idB = -11',
  ...
]

if __name__ == '__main__':
  mill = PythiaMill(SDetector(10, 10), options, cache_size=4, batch_size=16, n_workers=2)
  a = mill.sample()
```

`PythiaMill` arguments:
- detector (see section *Detectors*);
- `options` to be set in Pythia (as list of Python string), see Pythia manual;
- `cache_size` - number of batches in circulation in the mill (completed + in progress + enqueued batches), recommended value: 2 x number of workers;
- `batch_size` - number of events in batch, 


### Detectors

For performance reasons `PythiaMill` allows only fixed-size output. However, raw events are lists of particles without fixed size.
Additionally, event processing can be quite expensive, thus, it is more efficient if it is done in parallel.

The base class that transforms list of particles into a fixed-sized vector is called `Detector`.

There are currently 3 pre-installed detectors:

- `pythiamill.utils.SDetector`
  Spherical detector with a uniform grid along phi angle and specified pseudo-rapidity range.
- `pythiamill.utils.STDetector`
  Computes `Sphericity(2.0, 2)`, `Sphericity(1.0, 2)` and `Thrust(2)` whatever it means (see Pythia manual for details).
- `pythiamill.utils.TuneMCDetector`
  Extracts features analogous to the ones from "Event generator tuning using Bayesian optimization Philip Ilten, Mike Williams, Yunjie Yang arXiv:1610.08328" paper.
  The major difference is that all histograms are computed for only 1 event, i.e. features from the paper can be obtained as sum of feature vectors for a number of events.

### Seed

Don't forget option `'Random:seed=0'`!
For more information: [Pythia Manual](http://home.thep.lu.se/Pythia/pythia82html/RandomNumberSeed.html)

## Docker

Troubles with installation? Consult docker file. 

__Note PYTHIA_ADDITIONAL_FLAGS, your system might not support the default flags.__    