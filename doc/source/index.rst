=====================================================
qiprofile-rest: Quantitative Imaging Profile REST API
=====================================================

********
Synopsis
********
The Quantitative Imaging Profile REST API serves data for the
Quantitative Imaging Profile web application.

:API: http://quip1.ohsu.edu:8080/qiprofile-rest/api

:Git: git\@quip1.ohsu.edu:qiprofile-rest
      (`Browse <http://quip1.ohsu.edu:6060/qiprofile-rest>`__)


************
Installation
************
1. Install Git_ on your workstation, if necessary.

2. Contact the `OHSU QIN Git administrator`_ to obtain permission
   to access the ``qiprofile-rest`` Git repository.

3. Clone the Git repository::

       cd ~/workspace
       git clone git@quip1:qiprofile-rest
   
4. Install the Python_ pip_ package on your workstation, if necessary.
   
5. Install virtualenv_ package on your workstation, if necessary.

6. Install MongoDB_, if necessary.

7. Activate a new virtual environment, e.g.::

       virtualenv ~/qiprofile
       source ~/qiprofile/bin/activate

8. Install ``qiprofile-rest`:

       ./manage.py install


*****
Usage
*****

1. Start MongoDB::

       mongod&

2. Run the following command to display the REST server commands and options::

       ./manage.py --help

3. Start the REST server::

       ./manage.py runserver


---------

.. container:: copyright

  Copyright (C) 2014 Oregon Health & Science University `Knight Cancer Institute`_.
  All rights reserved.
  ``qiprofile-rest`` is confidential and may not be distributed in any form without
  authorization.


.. Targets:

.. _Django MongoDB Engine: http://django-mongodb-engine.readthedocs.org/en/

.. _django-nonrel Django clone: https://github.com/django-nonrel/django

.. _django-extensions: http://django-extensions.readthedocs.org

.. _Git: http://www.git-scm.com

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _MongoDB: http://django-mongodb.org

.. _OHSU QIN Git administrator: loneyf@ohsu.edu

.. _pip: https://pypi.python.org/pypi/pip

.. _Python: http://www.python.org

.. _virtualenv: http://www.virtualenv.org/


.. toctree::
  :hidden:
