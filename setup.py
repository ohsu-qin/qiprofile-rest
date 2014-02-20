import glob
from setuptools import (setup, find_packages)

def requires():
    with open('requirements.txt') as f:
        return f.read().splitlines()

def readme():
    with open("README.rst") as f:
        return f.read()

setup(
    name = 'qiprofile',
    version = '1.1.1',
    author = 'OHSU Knight Cancer Institute',
    author_email = 'loneyf@ohsu.edu',
    packages = find_packages(),
    scripts = glob.glob('bin/*'),
    url = 'http://quip1.ohsu.edu/8080/qiprofile',
    description = 'qiprofile is the REST API for the Imaging Profile web application.',
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
