.. _index:

=======================================
qiprofile: Quantitative Imaging Profile
=======================================

********
Synopsis
********
The Quantitative Imaging Profile web application displays imaging and clinical
data for the `OHSU QIN Sharepoint`_ study.

:API: http://quip1.ohsu.edu:8080/qiprofile/api

:Git: git\@quip1.ohsu.edu:qiprofile
(`Browse <http://quip1.ohsu.edu:6060/qiprofile>`__)


************
Feature List
************
1. OHSU QIN patient MR visualization.

2. ROI capture.

3. Clincial annotation editor.

4. qipipe_ pharmokinetic modeling result display.


************
Installation
************
1. Install Git_ on your workstation.

2. Contact the qiprofile `OHSU QIN Git administrator`_ to get permission
   to access the qipipe Git repository.

3. Clone the `qiprofile repository`_::

       cd ~/workspace
       git clone git@quip1:qiprofile
   
4. Install the Python_ pip_ package on your workstation.

5. Install the qiprofile package::

       cd ~/workspace/qiprofile
       pip install -e .


*****
Usage
*****
Run the following command to dispays the server commands and options::

     qiprofile --help

---------

.. container:: copyright

  Copyright (C) 2014 Oregon Health & Science University `Knight Cancer Institute`_.
  All rights reserved.
  ``qiprofile`` is confidential and may not be distributed in any form without authorization.


.. Targets:

.. _Git: http://git-scm.com

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _OHSU QIN Git administrator: loneyf@ohsu.edu

.. _OHSU QIN Sharepoint: https://bridge.ohsu.edu/research/knight/projects/qin/SitePages/Home.aspx

.. _pip: https://pypi.python.org/pypi/pip

.. _Python: http://www.python.org

.. _qipipe: http://quip1.ohsu.edu:8080/qipipe

.. _qiprofile repository: http://quip1.ohsu.edu:6060/qiprofile


.. toctree::
  :hidden:

  api/index
  api/helpers
  api/interfaces
  api/pipeline
  api/staging
