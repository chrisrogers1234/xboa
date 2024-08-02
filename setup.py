#!/usr/bin/env python
# NOTE -- when making distribution, distutils makes a MANIFEST folder
# subsequently distutils ignores new files - urk

import os
import sys
import xboa
from distutils.core import setup, Extension

prefix = os.path.join('/', sys.prefix, 'share' ,'xboa')
dfiles = [(prefix+'/doc/',  ['README']),
          (prefix+'/data/', [
           'xboa/examples/example_data/ecalc9f_for009_test.dat',
           'xboa/examples/example_data/ecalc9f_g4mice_test.dat',
           'xboa/examples/example_data/ecalc9f.inp',
           'xboa/examples/example_data/ecalc9f_prel.inp',
           'xboa/examples/example_data/ecalc9f_test.dat',
           'xboa/examples/example_data/for009.dat',
           'xboa/examples/example_data/for003_test.dat',
           'xboa/examples/example_data/maus_test.root',
           'xboa/examples/example_data/muon1_output.csv',
           'xboa/examples/example_data/test_config.dat'
           ]),
]

hitcore_mod = Extension(
    'xboa.core._hitcore', 
    sources = [
        'xboa/core/pylib/PyHitcore.cc',
        'xboa/core/cpplib/Hitcore.cc',
        'xboa/core/utils/SmartPointer.cc'
    ],
    include_dirs = ['xboa/core'],
)

weight_context_mod = Extension(
    'xboa.core._weight_context',
    sources = [
        'xboa/core/pylib/PyWeightContext.cc',
        'xboa/core/cpplib/WeightContext.cc',
    ],
    include_dirs = ['xboa/core'],
)

bunchcore_mod = Extension(
    'xboa.core._bunchcore',
    sources = [
        'xboa/core/pylib/PyBunchcore.cc',
        'xboa/core/cpplib/Bunchcore.cc',
        'xboa/core/cpplib/Hitcore.cc',
        'xboa/core/utils/SmartPointer.cc'
    ],
    include_dirs = ['xboa/core'],
)

setup(name='xboa',
      version=xboa.__version__,
      description='Cross-Platform Beam Optics Analysis - A multiparticle tracking postprocessor library for accelerator physicists',
      author='Chris Rogers',
      author_email='chris.rogers@stfc.ac.uk',
      url='http://micewww.pp.rl.ac.uk/projects/x-boa/wiki',
      packages=['xboa',
                'xboa.hit',
                'xboa.bunch',
                'xboa.bunch.weighting',
                'xboa.common',
                'xboa.hit.factory',
                'xboa.tracking',
                'xboa.tracking.tracking_process',
                'xboa.algorithms',
                'xboa.algorithms.peak_finder',
                'xboa.algorithms.closed_orbit',
                'xboa.algorithms.tune',
                'xboa.algorithms.smoothing',
                'xboa.core',
                'xboa.examples',
                'xboa.test',
      ],
      ext_modules = [hitcore_mod, bunchcore_mod, weight_context_mod],
      scripts=['xboa/examples/XBOA9f',
               'xboa/tracking/tracking_process/xboa_tracking_process.py'],
      data_files=dfiles,
      license='GPLv3',
      platforms='linux',
      python_requires='>3.0',
      long_description=\
"""
Cross-Platform Beam Optics Analysis
A multiparticle tracking postprocessor library for accelerator physicists.
You\'ve got your favourite tracking code running, what now? This package is a 
post-processor for taking beam data to calculate emittance, Twiss functions,
etc. Also includes bindings to plotting packages ROOT and matplotlib, and a 
whole lot more!
""",)


