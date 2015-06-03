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

   Alternatively, the server can be started in development mode with the
   ``--development`` option::
   
        qirest --development



4. The data model is described in the `REST client`_ documentation.
   The REST API is described in the `Eve Features`_ documentation. For
   example, the following command returns the JSON list of all subjects
   for a server running on the local machine::
   
       curl -i http://localhost:5000/subject


***********
Development
***********

Download the source by cloning the `source repository`_::

    git clone https://github.com/ohsu-qin/qiprofile-rest.git

Testing is performed with the nose_ package, which must be installed separately.

Documentation is built automatically by ReadTheDocs_ when the project is pushed
to GitHub. Documentation can be generated locally as follows:

* Install Sphinx_, if necessary.

* Run the following in the ``doc`` subdirectory::

      make html

A sample database can be created by running the following command in the local
``qiprofile-rest`` project directory::

    ./qiprofile_rest/test/helpers/seed.py

---------

.. container:: copyright


.. Targets:

.. _Eve Features: http://python-eve.org/features.html

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _MongoDB: http://django-mongodb.org

.. _nose: https://nose.readthedocs.org/en/latest/

.. _pip: https://pypi.python.org/pypi/pip

.. _Python: http://www.python.org

.. _source repository: https://github.com/ohsu-qin/qiprofile-rest

.. _REST client: qiprofile-rest-client.readthedocs.org/en/latest/

.. _QuIP: https://github.com/ohsu-qin/qiprofile

.. _ReadTheDocs: https://www.readthedocs.org

.. _Sphinx: http://sphinx-doc.org/index.html

