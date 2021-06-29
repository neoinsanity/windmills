"""Scaffold mix-in provides the means to add command-line configuration
options for the construction of *-windmill and app devices.
"""
import argparse
import logging
import os.path
from logging import DEBUG, ERROR, INFO, WARN
from .miller import Miller


__author__ = 'neoinsanity'
__all__ = ['Scaffold']


class Scaffold(Miller):
    """The Scaffold class is a helper mix-in that evaluates sys.argv into options
    settings for execution of windmill devices.

    Scaffold operates by testing for the 'argv' property presence in the
    kwargs dictionary passed in the __init__ method. If the 'argv' property
    is available then, Scaffold will then call configure_options and configure
    methods that may be defined on any progenitor base classes.

    Any classes sharing a base class chain with Scaffold may implement:
        - configure_options(self, arg_parser)
            arg_parser - is an argparse.ArgumentParser object that is used by
            each implementing base class to declare configuration options.
        - configure(self, args)
            args - is a property object that will be set with the keyword
            value results from parsing the configuration options.

    Of note is that Scaffold will cause the application to exit if the '-h'
    or '--help' configure arguments are one of the options. In addition to
    exiting, the child class will display the command line help message.
    """

    LOG_LEVEL_MAP = {
        'debug': DEBUG,
        'info': INFO,
        'warn': WARN,
        'error': ERROR
    }


    def __init__(self, argv=[]):
        """ Initializes the Scaffold support infrastructure.

        :param argv : An array of arguments of the form ['--verbose', '--name', 'my_name', ...]
        :return: A configured instance of Scaffold.

        A default Scaffold will assume the name of the instantiating class. In addition, it will
        not consider the name to have been set.
        >>> import logging
        >>> foo = Scaffold()
        >>> assert foo.name == 'Scaffold'
        >>> assert foo.name_set == False
        >>> assert foo.log_level == logging.ERROR
        >>> assert foo.log_path == None
        >>> assert foo.verbose == False

        A Scaffold can be configured utilizing the an array style argument list.
        >>> bar = Scaffold(['--name','Bar','--log_level','debug','--verbose'])
        >>> assert bar.name == 'Bar'
        >>> assert bar.name_set == True
        >>> assert bar.log_level == logging.DEBUG
        >>> assert bar.log_path == None
        >>> assert bar.verbose == True

        In addition, the Scaffold can be configured from a string.
        >>> dude = Scaffold('--name Dude --log_level info --log_path ../test/test_out')
        >>> assert dude.name == 'Dude'
        >>> assert dude.name_set == True
        >>> assert dude.log_level == logging.INFO
        >>> assert dude.log_path == '../test/test_out'
        >>> assert dude.verbose == False
        """
        self.log_level = 'error'
        self.log_path = None
        self.name = self.__class__.__name__
        self.name_set = False
        self.verbose = False

        # helper to allow using string for configuration
        if argv is not None and isinstance(argv, str):
            argv = argv.split() # convert string to args style list

        # determine if a name has benn set for the instantiating windmill instance
        if argv and '--name' in argv:
            self.name_set = True

        self._execute_configuration(argv)


    def configuration_options(self, arg_parser=None):
        arg_parser.add_argument('--log_level',
                                default=self.log_level,
                                choices=['debug', 'info', 'warning', 'error'],
                                help="Set the log level for the log output.")
        arg_parser.add_argument('--log_path',
                                default=self.log_path,
                                help='Set the path for log output. The default file created is '
                                     'the path/name.log. If the path ends with a ".log", then '
                                     'the path will assume a file path.')
        arg_parser.add_argument('--name',
                                default=self.name,
                                help='This will set the name for the current instance. The name '
                                     'is used for both log output and zmq socket identification')
        arg_parser.add_argument('--verbose',
                                action="store_true",
                                default=self.verbose,
                                help='Enable verbose log output. Useful for debugging.')


    def configure(self, args=None):
        assert args

        self._configure_logging()


    def _configure_logging(self):
        """This method configures the self.log entity for log handling.

        :return: None
        """
        self.log_level = Scaffold.LOG_LEVEL_MAP.get(self.log_level, ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # assign the windmill instance logger
        #logging.basicConfig()
        self.log = logging.getLogger(self.name)
        self.log.setLevel(self.log_level)

        if self.log_path:
            file_path = None
            if self.log_path.endswith('.log'):
                file_path = self.log_path
            else:
                file_path = os.path.join(self.log_path, self.name + '.log')
            assert file_path
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            self.log.addHandler(file_handler)

        # if we are in verbose mode, then we send log output to console
        if self.verbose:
            # add the console logger for verbose mode
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            self.log.addHandler(console_handler)

        self.log.info('Logging configured for: %s', self.name)


    def _execute_configuration(self, argv=None):
        """Collect and configure the configuration options for instantiation of Scaffold and child classes.

        This method operates by taking an argument list in ArgParse format and creating an argument
        list. The argument list is created by invoking the configuration_option method defined by
        each of the progenitor classes derived from Scaffold.

        :param argv: A list of arguments of the form ['--verbose', '--name', 'my-name', ...]

        This test shows how the
        >>> foo = Scaffold()
        >>> argv = [
        ... '/Users/neoinsanity/samples/samples/my-argparse/simpe_argparse.py',
        ... '--verbose']
        >>> foo._execute_configuration(argv=argv)
        >>> assert foo.verbose == True
        """
        if argv is None:
            argv = [] # just create an empty arg list

        arg_parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        # if this is the command line args directly, them we need to remove the
        # first argument which is the python execution command. it is
        if len(argv) > 0 and argv[0].endswith('.py'):
            argv.pop(0)

        # gather argument options
        self.__invoke_method_on_bases__(func_name='configuration_options',
                                        arg_parser=arg_parser)
        property_list = []
        for action in arg_parser._get_optional_actions():
            property_list.append(action.dest)
        property_list.remove('help') # remove the help option, as it is not necessary
        self._args = arg_parser.parse_args(argv)
        # map the properties to attributes assigned self instance
        self.__copy_property_values__(src=self._args,
                                      target=self,
                                      property_list=property_list)
        # now execute the configuration call on each base class
        # in the class inheritance chain
        self.__invoke_method_on_bases__(func_name='configure',
                                        args=self._args)

        self.log.info('... scaffold configuration complete ...')
