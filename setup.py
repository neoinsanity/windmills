from distutils.core import setup


setup(
    name='windmill',
    version='0.0.1',
    packages=['', 'lib'],
    package_dir={'': 'windmills', 'lib':'windmills/lib'},
    url='https://github.com/neoinsanity/windmills',
    license='Apache License 2.0',
    author='Raul Gonzalez',
    author_email='novum.insania@gmail.com',
    description='This is a set of tools and libraries focused on creating 0mq'
                ' solutions.',
    requires=['pyzmq',]
)
