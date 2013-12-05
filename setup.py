from setuptools import setup

# The list of required packages to run Windmills.
requires = [
  'gevent==1.0',
  'greenlet==0.4.1',
  'pyzmq==14.0.1',
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
  packages=['windmills'],
  install_requires=requires,
)
