#!/usr/bin/env python

from setuptools import find_packages, setup

setup(name='common',
      version='1.0',
      install_requires=[
          'gql[all]',
          'backoff',
          'asyncio',
      ],
      packages=find_packages(include=['common', 'common.*']),
      )
