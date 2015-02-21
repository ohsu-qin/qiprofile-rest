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

   In order to start the server in development mode, use the ``--development``
   option::
   
        qirest --development


***********
Development
***********

Testing is performed with the nose_ package, which must be installed separately.

Documentation is built automatically by ReadTheDocs_ when the project is pushed
to GitHub. Documentation can be generated locally as follows:

* Install Sphinx_, if necessary.

* Run the following in the ``doc`` subdirectory::

      make html

---------

.. container:: copyright

  Copyright (C) 2014 Oregon Health & Science University `Knight Cancer Institute`_.
  All rights reserved.


.. Targets:

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _MongoDB: http://django-mongodb.org

.. _nose: https://nose.readthedocs.org/en/latest/

.. _pip: https://pypi.python.org/pypi/pip

.. _Python: http://www.python.org

.. _QuIP: https://github.com/ohsu-qin/qiprofile

.. _ReadTheDocs: https://www.readthedocs.org

.. _Sphinx: http://sphinx-doc.org/index.html

