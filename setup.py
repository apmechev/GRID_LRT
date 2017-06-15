#!/usr/bin/env python

from distutils.core import setup

setup(name='GRID_LRT',
      version='0.2',
      description='Grid LOFAR Reduction Tools',
      author='Alexandar Mechev',
      author_email='apmechev@strw.leidenuniv.nl',
##      url='https://www.python.org/sigs/distutils-sig/',
      setup_requires=[
        'pytest-runner',
    ],
      tests_require=[
        'pytest',
    ],
      packages=['GRID_LRT','GRID_LRT/LRTs','GRID_LRT/Staging'] 
     )

