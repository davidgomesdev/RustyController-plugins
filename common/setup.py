#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(name='common',
      version='1.0',
      install_requires=[
          'gql[all]',
          'backoff',
          'asyncio',
      ],
      packages=find_packages(include=['common', 'common.*']),
      )
