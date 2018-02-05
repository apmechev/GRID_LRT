************
Installation
************

Via Python Package (coming soon)
==================

Install the package (or add it to your ``requirements.txt`` file):

.. code:: bash

    pip install GRID_LRT


Via Git or Download
===================

Download the latest version from ``https://www.github.com/apmechev/GRID_LRT``. To install, use 

.. code:: bash 

    python setup.py build
    python setup.py install

In the case that you do not have access to the python system libraries, you can use ``--prefix=`` to specify install folder. For example if you want to install it into a folder you own (say /home/apmechev/software/python) use the following command:

.. code:: bash

    python setup.py build
    python setup.py install --prefix=/home/apmechev/software/python


NOTE: you need to have your pythonpath containing "/home/apmechev/software/python/lib/python$(PYTHON_VERSION)/site_packages" and that folder needs to exist beforehand or setuptools will complain


