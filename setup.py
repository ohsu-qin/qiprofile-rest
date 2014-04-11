import os
import re
import glob
from setuptools import (setup, find_packages)


def version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
    

def requires():
    with open('requirements.txt') as f:
        return f.read().splitlines()


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
