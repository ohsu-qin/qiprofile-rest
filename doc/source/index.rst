.. _index:

================================================
qiprofile: Quantitative Imaging Profile REST API
================================================

********
Synopsis
********
The Quantitative Imaging Profile REST API serves data for the
`Quantitative Imaging Profile`_ web application.

:API: http://quip1.ohsu.edu:8080/qiprofile-rest/api

:Git: git\@quip1.ohsu.edu:qiprofile-rest
(`Browse <http://quip1.ohsu.edu:6060/qiprofile-rest>`__)


************
Installation
************
1. Install Git_ on your workstation.

2. Contact the `OHSU QIN Git administrator`_ to obtain permission
   to access the ``qiprofile-rest`` Git repository.

3. Clone the `qiprofile-rest repository`_::

       cd ~/workspace
       git clone git@quip1:qiprofile-rest
   
4. Install the Python_ pip_ package on your workstation.

5. Install the ``qiprofile-rest`` package::

       cd ~/workspace/qiprofile-rest
       pip install -e .


*****
Usage
*****
Run the following command to dispays the server commands and options::

     ./manage.py --help

---------

.. container:: copyright

  Copyright (C) 2014 Oregon Health & Science University `Knight Cancer Institute`_.
  All rights reserved.
  ``qiprofile-rest`` is confidential and may not be distributed in any form without
  authorization.


.. Targets:

.. _Git: http://www.git-scm.com

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _OHSU QIN Git administrator: loneyf@ohsu.edu

.. _pip: https://pypi.python.org/pypi/pip

.. _Python: http://www.python.org

.. _qiprofile-rest: http://quip1.ohsu.edu:8080/qiprofile-rest

.. _qiprofile-rest repository: http://quip1.ohsu.edu:6060/qiprofile-rest
