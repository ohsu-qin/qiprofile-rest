=====================================================
qiprofile-rest: Quantitative Imaging Profile REST API
=====================================================

********
Synopsis
********
The Quantitative Imaging Profile REST API serves data for the
`Quantitative Imaging Profile`_ web application.

:API: https://readthedocs.org/projects/qiprofile-rest/

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

.. _Quantitative Imaging Profile: https://github.com/ohsu-qin/qiprofile

.. toctree::
  :hidden:
  
  api/index

