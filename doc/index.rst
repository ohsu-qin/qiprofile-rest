========================================================
qiprofile-rest: Quantitative Imaging Profile REST server
========================================================

********
Synopsis
********
The Quantitative Imaging Profile REST server serves data for the
QuIP_ (antitative Imaging Profile) web application.

:API: https://qiprofile-rest.readthedocs.org/en/latest/api/index.html

:Git: https://github.com/ohsu-qin/qiprofile-rest


************
Installation
************
1. Install the Python_ pip_ package on your workstation, if necessary.

2. Install MongoDB_, if necessary.

3. Install ``qiprofile-rest``::

       pip install qiprofile-rest


*****
Usage
*****

1. Start MongoDB::

       mongod&

2. Run the following command to display the REST server commands and options::

       qirest --help

3. Start the REST server::

       qirest


---------

.. container:: copyright

  Copyright (C) 2014 Oregon Health & Science University `Knight Cancer Institute`_.
  All rights reserved.


.. Targets:

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _MongoDB: http://django-mongodb.org

.. _pip: https://pypi.python.org/pypi/pip

.. _Python: http://www.python.org

.. _QuIP: https://github.com/ohsu-qin/qiprofile

.. toctree::
  :hidden:
  
  api/index

