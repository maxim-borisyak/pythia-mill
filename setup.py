"""
  Pythia Mill
"""

from setuptools import setup, find_packages, Extension

from codecs import open
import os
import os.path as osp
import numpy as np
import subprocess as sp

def get_includes():
  env = os.environ

  includes = []

  for k in ['CPATH', 'C_INCLUDE_PATH', 'INCLUDE_PATH', 'PYTHIA_INCLUDE']:
    if k in env:
      includes.append(env[k])

  return includes

def get_library_dirs():
  env = os.environ

  libs = []

  for k in ['LD_LIBRARY_PATH', 'PYTHIA_LIB']:
    if k in env:
      libs.append(env[k])

  return libs

from Cython.Build import cythonize

here = osp.abspath(osp.dirname(__file__))

with open(osp.join(here, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

extra_compile_args=['-std=c++98', '-Ofast', '-D_GLIBCXX_USE_CXX11_ABI=0', '-g']
extra_link_args=['-g']

def discover_cython(root):
  import os
  import os.path as osp

  def path_to_module(path: str, filename: str):
    rpath = osp.relpath(path, root)
    module = filename.split('.')[0]
    return '%s.%s' % (rpath.replace(osp.sep, '.'), module)

  for path, _, files in os.walk('src'):
    for file in files:
      if file.endswith('.pyx'):
        yield Extension(
          path_to_module(path, file), [osp.join(path, file)],
          libraries=['stdc++', 'pythia8'],
          include_dirs=[np.get_include()] + get_includes(),
          library_dirs=get_library_dirs(),
          language='c++',
          extra_compile_args=extra_compile_args
        )


extensions = [
  Extension(
    'pythiamill.utils.pythiautils', ['src/pythiamill/utils/pythiautils.pyx'],
    libraries=['stdc++', 'pythia8'],
    include_dirs=[np.get_include()] + get_includes(),
    library_dirs=get_library_dirs(),
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
  ),

  Extension(
    'pythiamill.utils.detector', ['src/pythiamill/utils/detector.pyx'],
    libraries=['stdc++', 'pythia8'],
    include_dirs=[np.get_include()] + get_includes(),
    library_dirs=get_library_dirs(),
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
  ),

  Extension(
    'pythiamill.utils.sdetector', ['src/pythiamill/utils/sdetector.pyx'],
    libraries=['stdc++', 'pythia8'],
    include_dirs=[np.get_include()] + get_includes(),
    library_dirs=get_library_dirs(),
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
  ),

  Extension(
    'pythiamill.utils.stdetector', ['src/pythiamill/utils/stdetector.pyx'],
    libraries=['stdc++', 'pythia8'],
    include_dirs=[np.get_include()] + get_includes(),
    library_dirs=get_library_dirs(),
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
  ),

  Extension(
    'pythiamill.utils.spherical_tracker', ['src/pythiamill/utils/spherical_tracker.pyx'],
    libraries=['stdc++', 'pythia8'],
    include_dirs=[np.get_include()] + get_includes(),
    library_dirs=get_library_dirs(),
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
  ),

  Extension(
    'pythiamill.utils.pseudo_velo', ['src/pythiamill/utils/pseudo_velo.pyx'],
    libraries=['stdc++', 'pythia8'],
    include_dirs=[np.get_include()] + get_includes(),
    library_dirs=get_library_dirs(),
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
  ),

  Extension(
    'pythiamill.utils.tunemcdetector', [
      'src/pythiamill/utils/tunemcdetector.pyx',
      'src/pythiamill/utils/TuneMC.cpp',
    ],
    libraries=['stdc++', 'pythia8'],
    include_dirs=[np.get_include()] + get_includes(),
    library_dirs=get_library_dirs(),
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args
  )
]

setup(
  name='pythia-mill',

  version='1.0.0',

  description="""Pythia generator for python.""",

  long_description = long_description,

  url='https://github.com/maxim-borisyak/pythia-mill',

  author='Maxim Borisyak',
  author_email='mborisyak at yandex-team dot ru',

  maintainer = 'Maxim Borisyak',
  maintainer_email = 'mborisyak at yandex-team dot ru',

  license='MIT',

  classifiers=[
    'Development Status :: 4 - Beta',

    'Intended Audience :: Science/Research',

    'Topic :: Scientific/Engineering :: Physics',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
  ],

  keywords='Pythia',

  packages=find_packages('src'),
  package_dir={'': 'src'},

  extras_require={
    'dev': ['check-manifest'],
    'test': ['nose>=1.3.0'],
  },

  install_requires=[
    'numpy',
    'cython'
  ],

  include_package_data=True,

  package_data = {
  },

  ext_modules = cythonize(
    extensions,
    gdb_debug=True,
    compiler_directives={
      'embedsignature': True
    }
  ),
)
