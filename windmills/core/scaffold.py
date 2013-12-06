"""The *Scaffold* class provides the means to add some basic features for
construction of service modules.

.. default-domain::py

For details, be sure to checkout the features described under the
:ref:`scaffold_class_utilization` section.:

- :ref:`configuration_management_and_initialization`

- :ref:`command_and_log_configuration`

- :ref:`dynamic_service_naming`

The intent is for *Scaffold* to make your life easier in the implementation
of stand alone applications. The hope is to take some common service
requirements and make the expression of those requirements trivial.

.. _scaffold_class_utilization:

Scaffold Class Utilization
===========================

*Scaffold* operates by accepting an *argv* passed in the
:meth:'^windmills.core.Scaffold.__init__ method`. During the initialization
of instance based on *Scaffold* derived class, *Scaffold* will drive
configuration by applying *argv* options to instance **self**.

By way of example, let's construct a hello world example. First we define
*HelloWorld* class as below:

.. _hello_world_class:
.. code-block:: python
  :linenos:

  from windmills.core import Scaffold
  import sys

  class HelloWorld(Scaffold):
    def __init__(self, **kwargs):
      self.response = 'Hello World'

      # !!! Very important, Do NOT forget. !!!
      Scaffold.__init__(self, **kwargs)

    def configuration_options(self, arg_parser):
      arg_parser.add_argument('-response', default=self.response)

    def configure(self, args):
      if(args.response != 'Hello World':  # is default value
        self.response += ' You Rascal!'

    def run(self):
      print self.response

  if __name__ == '__main__':
    helloWorld = HelloWorld(argv=sys.argv)
    helloWorld.run

This gives the class hierarchy as in the image below.

.. figure:: ../images/scaffold_utilization_example_hierarchy.png

  Scaffold Example Hierarchy

The essence of how *Scaffold* performs it's operations is via the use of
:mod:`windmills.core.miller` module to derive configuration of service stack.
The basic call sequence is depicted in the image below.

.. image:: ../images/scaffold_utilization_example_sequence.png

:meth:`~windmills.core.Scaffold.configuration_options` and
:meth:`~windmills.core.Scaffold.configure` methods via the use of the
:meth:`windmills.core.Miller.__invoke_method_on_children__'. This effectively
calls the *configure_options* and *configure* methods on all primary base
classes that derive from *Scaffold*.

** _configuration_management_and_initialization:

Configuration Management and Initialization
=============================================

*Scaffold* helps out with configuration management and initialization of
runtime services. it does this by creating a configuration loop. Utilizing the
:ref:`hello_world_class` as an example.

.. _command_line_option_construction:

Command Line Option Construction
---------------------------------

*Scaffold* provides the means for command line construction to inheriting
classes. This is achieved by the ingestion of command line options through
invocation of *configure_option* method on the chain of ancestor classes that
declare the *configuration_option* method.

The net effect is that *Scaffold* will collect all of the configuration
options in one bundle, and manage them as a unified instance configuration.
This allows for the centralization of common options and the attending code.

For more detail on this feature, be sure to check out
:meth:`~windmills.core.Scaffold._execute_configuration`.

.. _logging_and_log_configuration

Logging and Log Configuration
------------------------------

*Scaffold* supports console and file output. In addition *Scaffold* supports
the four basic log levels: `debug`,`info`,`warning`,`error`.

The configuration logging options are:

  :arg: --log_level {debug,info,warning,error}

    Set the log level for the log output.

  :arg: --log_path LOG_PATH

    Set the path for log output. The default file created is
    "<log_path>/<app_name>.log". If the path ends with a ".log"
    extension, then the path be a target file.

  :arg: --verbose

    Enable verbose log output to console. Useful for debugging.

*Scaffold* log configuration takes advantage of the
:ref:`dynamic_service_naming` for log file naming, as well as in log name
output.

For example::

  2012-12-02 03:26:03,030 - <name> - INFO - Logging configured for: VentilatorWindmill

The <name> value will be assigned by default to the instance class utilizing
*Scaffold*, but will be overridden by the use of the '--app_name <name>'
option.


.. _dynamic_service_naming:

Dynamic Service Naming
------------------------

*Scaffold* provides a mechanism to allow for dynamic naming of progenitor class
service instances. This is achieved through the use of the '--app_name <name>'
option. When this flag is set *Scaffold* will set the `self.name` instance to
the designated value. In addition, *Scaffold* will set the `self.name_set`
flag to `True`.

By default *Scaffold* will set the name of the instance class.

The assigned name can effect the output log name, as well as name of the log
output. The use of `self.name` may also effect features from other progenitor
classes that take advantage of *Scaffold* dynamic naming.

Child classes of Scaffold can access the configured service app name through
`self.app_name`.
"""
import argparse
import logging
from logging.handlers import WatchedFileHandler
import os
import shlex

from miller import Miller

__author__ = 'Raul Gonzalez'


class Scaffold(Miller):
  """The *Scaffold* class is a helper mix-in that evaluates sys.argv into
  options settings for execution of windmill devices.

  :Command Line Usage:

  *Scaffold* supports the following command line options::

    usage: <some_class>.py [-h] [--log_level {debug,info,warn,error}]
                        [--log_path LOG_PATH] [--app_name APP_NAME] [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --log_level {debug,info,warning,error}
                            Set the log level for the log output.
      --log_path LOG_PATH   Set the path for log output. The default file
                            created is the path/name.log. If the path ends
                            with a ".log", then the path will assume a file
                            path.
      --name NAME           This will set the name for the current instance.
                            The name is used for both log output and zmq socket
                            identification
      --verbose             Enable verbose log output to console. Useful for
                            debugging.


  .. note:: *Scaffold* will cause the application to exit if the ``-h``
    or ``--help`` configure arguments are one of the options. In addition to
    exiting, *Scaffold* will display the command line help message.

  Any classes sharing a base class chain with *Scaffold* may implement:

    - configure_options(self, arg_parser)

    - configure(self, args)

  This method operates by taking an options list in *argparse* format and
  creates an argument list. The argument list is generated by processing
  *argv* through *argparse.ArgumentParser*. The resultant arguments are
  applied to `self`.

  .. note: File name sniffing.

    The argument list that is obtained from *sys.argv* will have the path of
    the invoking python file. For purposes of *Scaffold* configuration this
    argument is irrelevant. The *_execute_configuration* method will detect
    the for this state and removes the path argument.
  """
  #: A map for setting ``logging`` level upon log configuration during
  #: invocation of :meth:`~windmills.core.Scaffold._
  LOG_LEVEL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'error': logging.ERROR,
  }

  def __init__(self, argv=list()):
    """ Initializes the Scaffold support infrastructure.

    :param argv: An array of arguments of the form
                 ['--verbose', '--name', 'my_name', ...]
    :type argv: String | String List
    :return: `Scaffold` child instance

    A default Scaffold will assume the name of the instantiating class. In
    addition, it will not consider the name to have been set.

    >>> class Foo(Scaffold):
    ...     def __init__(self, **kwargs):
    ...         Scaffold.__init__(self, **kwargs)
    >>> foo = Foo()
    >>> assert foo.app_name == 'Foo'
    >>> assert foo.app_name_set == False
    >>> assert foo.log_level == logging.ERROR
    >>> assert foo.log_path == None
    >>> assert foo.verbose == False

    A Scaffold can be configured utilizing the an array style argument list.

    >>> bar = Scaffold(['--app_name','Bar','--log_level','debug'])
    >>> assert bar.app_name == 'Bar'
    >>> assert bar.app_name_set == True
    >>> assert bar.log_level == logging.DEBUG
    >>> assert bar.log_path == None
    >>> assert bar.verbose == False

    In addition, the Scaffold can be configured from a string.

    >>> dude = Scaffold(
    ...   '--app_name Dude --log_level info')
    >>> assert dude
    >>> assert dude.app_name == 'Dude'
    >>> assert dude.app_name_set == True
    >>> assert dude.log_level == logging.INFO
    >>> assert dude.verbose == False
    """
    #: Current log level, set to logging.DEBUG, INFO, WARNING, OR ERROR at
    #: runtime.
    self.log_level = 'error'
    #: The path to the log file, if one is set.
    self.log_path = None
    #: The name of the application. Overridden by '--app_name' option.
    self.app_name = self.__class__.__name__
    #: Set to true if the '--app-name' is utilized
    self.app_name_set = False
    #: Set to true if '--verbose' option flag is utilized
    self.verbose = False

    #: The log attribute to use for logging message
    self.log = None
    # helper to allow using string for configuration
    if argv is not None and isinstance(argv, basestring):
      argv = shlex.split(argv)  # convert string to args style list

    # determine if a name has been set for the instantiating class instance
    if argv and '--app_name' in argv:
      self.app_name_set = True

    self._execute_configuration(argv)

  def configuration_options(self, arg_parser=argparse.ArgumentParser()):
    """This method will be called to get the *Scaffold* configuration options.

    :param arg_parser: An *ArgumentParser* instance to add configuration
                       options.
    :type arg_parser: `argparse.ArgumentParser`
    :return: None
    """
    arg_parser.add_argument('--app_name',
                            default=self.app_name,
                            help='This will set the name for the current '
                                 'instance. This will be reflected in the log '
                                 'output.')
    arg_parser.add_argument('--log_level',
                            default=self.log_level,
                            choices=['debug', 'info', 'warn', 'error'],
                            help='Set the log level for the log output.')
    arg_parser.add_argument('--log_path',
                            default=self.log_path,
                            help='Set the path for log output. The default '
                                 'file created is "<log_path>/<app_name>.log"'
                                 '. If the path ends with a ".log" extension,'
                                 ' then the path be a target file.')
    arg_parser.add_argument('--verbose',
                            action='store_true',
                            default=self.verbose,
                            help='Enable verbose log output to console. '
                                 'Useful for debugging.')

  def configure(self, args=None):
    """ This method is called by *Scaffold* during instance initialization.

    :param args: An object with configuration properties.
    :type args: Property Object
    :return: None

    .. note:: Properties set to `self`.

      In addition to setting the configuration options to *self*, the *args*
      parameter has the configuration. This should allow for most complex
      configuration scenarios.
    """
    assert args

    self._configure_logging()

  def _configure_logging(self):
    """This method configures the self.log entity for log handling.

    :return: None

    The method will configure the logging facilities for the derive service
    instance. This includes setting up logging to files and console. The
    configured log will be available to the service instance with `self.log`
    """
    self.log_level = Scaffold.LOG_LEVEL_MAP.get(self.log_level, logging.ERROR)

    # if log level is debug, then we add source information to log output
    formatter = logging.Formatter(
      '%(asctime)s -%(name)s - %(levelname)s -- %(message)s')
    if self.log_level == logging.DEBUG:
      formatter = logging.Formatter(
        '%(asctime)s -%(name)s - %(levelname)s -- %(pathname)s:%(lineno)d '
        '-- %(message)s')

    # assign the windmill instance logger
    self.log = logging.getLogger(self.app_name)
    self.log.setLevel(self.log_level)

    # configure log file output if necessary
    if self.log_path:
      file_path = self.log_path
      if not self.log_path.endswith('.log'):
        file_path = os.path.join(self.log_path, self.app_name + '.log')

      file_handler = WatchedFileHandler(file_path)
      file_handler.setLevel(self.log_level)
      file_handler.setFormatter(formatter)
      self.log.addHandler(file_handler)

    # if we are in verbose mode, the we send log output to console
    if self.verbose:
      # add the console logger for verbose mode
      console_handler = logging.StreamHandler()
      console_handler.setLevel(self.log_level)
      console_handler.setFormatter(formatter)
      self.log.addHandler(console_handler)

    self.log.info('Logging configured for: %s', self.app_name)


  def _execute_configuration(self, argv=None):
    """This method assigns an argument list to attributes assigned to self.

    :param argv: A list of arguments.
    :type argv: string list
    :return: None

    This is the work horse method that does the work of invoking
    *configuration_option* and *configure* methods on progenitor classes of
    *Scaffold*. In addition it takes the resolved
    arguments from *argparse.ArgumentParser* and assigns them to `self`.

    :Example Usage:

    >>> foo = Scaffold()
    >>> argv = [
    ... '/Users/neoinsanity/samples/samples/my-argparse/simple_argparse.py',
    ... '--verbose']
    >>> foo._execute_configuration(argv=argv)
    >>> assert foo.verbose == True
    """
    if argv is None:
      argv = []  # just create an empty arg list

    arg_parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # if this is the command line args directly, then we need to remove the
    # first argument which is the python execution command. The first
    # argument is the name of the executing python script.
    if len(argv) > 0 and argv[0].endswith('.py'):
      argv.pop(0)

    # execute configuration_option method on all child classes of Scaffold
    # to gather all of the runtime options.
    self.__invoke_method_on_children__(func_name='configuration_options',
                                       arg_parser=arg_parser)

    # resolve configuration options necessary for runtime execution
    property_list = []
    #noinspection PyProtectedMember
    for action in arg_parser._get_positional_actions():
      property_list.append(action.dest)
      #noinspection PyProtectedMember
    for action in arg_parser._get_optional_actions():
      property_list.append(action.dest)
    property_list.remove('help')  # remove the help option
    args = arg_parser.parse_args(argv)

    # map the properties to attributes assigned to self instance
    self.__copy_property_values__(src=args,
                                  target=self,
                                  property_names=property_list)

    # now execute the configuration call on each base class
    # in the class inheritance chain
    self.__invoke_method_on_children__(func_name='configure',
                                       args=args)

    self.log.info('... scaffold configuration complete ...')
    self.log.info('... configuration: %s', args)

