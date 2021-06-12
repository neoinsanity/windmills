#!/usr/bin/env python
from setuptools import setup

# The list of required packages to run Windmills.
requires = [
  'gevent==21.1.2',
  'greenlet==1.1.0',
  'pyramid==2.0',
  'pyramid-jinja2==2.8',
  'pyzmq==22.1.0',
  'schematics==2.1.0',
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
