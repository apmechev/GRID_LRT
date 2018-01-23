#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
import os
setup(name='GRID_LRT',
      version='0.2',
      description='Grid LOFAR Reduction Tools',
      author='Alexandar Mechev',
      author_email='apmechev@strw.leidenuniv.nl',
##      url='https://www.python.org/sigs/distutils-sig/',
      setup_requires=[
        'pyyaml', 
    ],
      tests_require=[
        'pytest',
    ],
      data_files = [(root, [os.path.abspath(os.path.join(root, f)) for f in files])
                  for root, dirs, files in os.walk('GRID_LRT/Sandbox')],
      packages=['GRID_LRT','GRID_LRT/LRTs','GRID_LRT/Staging', 'GRID_LRT/Application', 'GRID_LRT/couchdb'] 
     )

