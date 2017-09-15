#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from setuptools import find_packages
from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='uber_rides',
    version='0.6.0',
    packages=find_packages(),
    description='Official Uber API Python SDK',
    long_description=readme,
    url='https://github.com/uber/rides-python-sdk',
    license='MIT',
    author='Uber Technologies, Inc.',
    author_email='dev-advocates@uber.com',
    install_requires=['requests', 'pyyaml'],
    extras_require={
        ':python_version == "2.7"': ['future'],
    },
    tests_require=['pytest', 'mock', 'vcrpy'],
    keywords=['uber', 'api', 'sdk', 'rides', 'library'],
)
