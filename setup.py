#!/usr/bin/env python
from setuptools import setup

# The list of required packages to run Windmills.
requires = [
  'gevent==1.0',
  'greenlet==0.4.1',
  'pyramid==1.4.5',
  'pyramid-jinja2==1.9',
  'pyzmq==14.0.1',
  'schematics==0.9-4',
  'wsgiref==0.1.2',
]

setup(
  name='windmills',
  version='0.2.0',
  url='https://github.com/neoinsanity/windmills',
  license='Apache License 2.0',
  author='Raul Gonzalez',
  author_email='mindbender@gmail.com',
  description='This is a set of tools and libraries focused on creating 0mq'
              ' based solutions.',
  packages=['windmills',
            'windmills.core',
            'windmills.core.super_core',
            'windmills.utility_service'],
  install_requires=requires,
)
