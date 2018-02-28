#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
import os

setup(name='GRID_LRT',
      packages=['GRID_LRT','GRID_LRT/Staging', 'GRID_LRT/Application', 'GRID_LRT/couchdb'],
      version='0.2.1',
      setup_requires=[
        'pyyaml', 
          ],
      tests_require=[
        'pytest', 
          ],
      description='GRID LOFAR Reduction Tools',
      long_description="Software that encapsulates LOFAR processing and allows the use of High Throughput Distributed processing available at SURFsara and other European Grid Initiative locations.",
      author='Alexandar Mechev',
      author_email='apmechev@strw.leidenuniv.nl',
      url='https://www.github.com/apmechev/GRID_LRT/',
      download_url = 'https://github.com/apmechev/GRID_LRT/archive/v0.2.0.tar.gz',
      keywords = ['surfsara', 'distributed-computing', 'LOFAR'],
      classifiers = ['Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Intended Audience :: Science/Research',
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)" ,
      "Natural Language :: English",
      "Topic :: Scientific/Engineering :: Astronomy",
      "Topic :: System :: Distributed Computing",
#      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',],
 
      data_files = [(root, [os.path.abspath(os.path.join(root, f)) for f in files])
                             for root, dirs, files in os.walk('GRID_LRT/Sandbox')]+ 
                    [("", ["LICENSE.txt"])]+
                    [(root, [os.path.abspath(os.path.join(root, f)) for f in files])
                                    for root, dirs, files in os.walk('config')]
     )

