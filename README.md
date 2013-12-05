Windmills
===========

This project is an attempt to create a library that will make it easy to
construct managed messageing patterns based on ZeroMq.

Note: The commands for this documentation are executed from the PROJECT_ROOT
directory. This would be the directory that contains this README.md file.

Setting up the Development Environment
----------------------------------------

Requirements:

  - ZMQ => 14.0.0
    This project is based on utilizing ZMQ. In most cases you only need to
    run the deployment script descried below, and you should be fine. If you
    run into any issues for you particular OS, be sure to checkout the Zmq
    website for instructions for assistance.
    http://zeromq.org/intro:get-the-software).

  - Virtualenv => 10.0.0.1
    The project assumes that virtualenv is being utilized in development to
    aid in minimizing dependency issues due to lib versions. If you choose
    not to utilize virtualenv, the you will need to setup the development
    environment manually. This amounts to executing the commands in the setup
    script minus the virutalenv specific commands. To install virtualenv,
    see the installation instructions on the virtualenv website.
    https://pypi.python.org/pypi/virtualenv

  - libevent => 2.0.21
    For OS X users, you will need to install this library using Homebrew. The
     brew install command is:

      brew install libevent

    If you need to install Homebrew, for you OS X developers, you can visit
    http://brew.sh/

Setup Dev Environment:

  The setup script is run from the Windmills project root directory.:

    /PROJECT_ROOT> bin/dev_setup.sh

  You can now type:

    /PROJECT_ROOT> . venv/bin/activate

  This command will place you into a virtualenv that can be used for
  development, without contaminating your development box.

Test Execution:

  To execute the tests, make sure that virtualenv for Windmill project is
  activated. The type the command:

    /PROJECT_ROOT> bin/run_test.sh

  This command will also create a coverage report that can be viewed at:

    /PROJECT_ROOT/COVERAGE_REPORT

  Testing is based on the use of nose test runner. This makes it convenient
  for executing tests individually. If you need to run an individual doctest,
   utilize the command as exampled:

   /PROJECT_ROOT> > nosetests --with-doctest windmills/core/miller.py

   For more info, on nose command options, visit:

    http://nose.readthedocs.org/en/latest/

