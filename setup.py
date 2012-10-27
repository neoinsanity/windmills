#!/usr/bin/env python
from distutils.core import setup


setup(
    name='windmills',
    version='0.0.1',
    url='https://github.com/neoinsanity/windmills',
    license='Apache License 2.0',
    author='Raul Gonzalez',
    author_email='novum.insania@gmail.com',
    description='This is a set of tools and libraries focused on creating 0mq'
                ' solutions.',
    packages=['windmills', 'windmills.lib'],
    requires=['pyzmq','ujson' ],
)
