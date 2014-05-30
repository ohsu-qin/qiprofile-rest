import os
import re
import glob
from setuptools import (setup, find_packages)
from pip.req import parse_requirements

def version(package):
    """
    Return package version as listed in the `__init__.py` `__version__`
    variable.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
    

def requires():
    valid_re = re.compile('[-\w]+(==[-\w.]+)?$')
    with open('requirements.txt') as f:
      entries = f.read().splitlines()
    return [entry for entry in entries if valid_re.match(entry)]


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name = 'qiprofile-rest',
    version = version('qiprofile_rest'),
    author = 'OHSU Knight Cancer Institute',
    author_email = 'loneyf@ohsu.edu',
    packages = find_packages(),
    scripts = glob.glob('bin/*'),
    url = 'http://quip1.ohsu.edu/8080/qiprofile-rest',
    description = 'qiprofile-rest is the REST API for the Imaging Profile web application.',
    long_description = readme(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Environment :: Web Environment',
        'Framework :: Django'
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English'
    ],
    install_requires = requires()
)
