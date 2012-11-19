"""Scaffold mix-in provides the means to add command-line configuration
options for the construction of *-windmill and app devices.
"""
import argparse
import logging
from logging import DEBUG, ERROR, INFO, WARN
from miller import Miller


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
        = configure(self, args)
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


    def __init__(self, argv=[], **kwargs):
        """ Initializes the Scaffold support infrastructure.


        :param argv : An array of arguments of the form ['--verbose', '--name', 'my_name'
        :param kwargs: The kwargs that are passed down for initialization. The
        :return:
        """
        self.log_level = 'error'
        self.name = self.__class__.__name__
        self.name_set = False
        self.verbose = False

        # if there is an argv argument, then use it to set the configuration
        #if 'argv' in kwargs and kwargs.get('argv') is not None:
        if argv is not None:
            #argv = kwargs['argv']
            if '--name' in argv:
            # determine if a name has benn set for the instantiating windmill instance
                self.name_set = True

        self._execute_configuration(argv)


    def configuration_options(self, arg_parser=None):
        arg_parser.add_argument('--log_level',
                                default=self.log_level,
                                choices=['debug', 'info', 'warning', 'error'],
                                help="Set the log level for the log output.")
        arg_parser.add_argument('--name',
                                default=self.name,
                                help='This will set the name for the current instance. The name '
                                     'is used for both log output and zmq socket identification')
        arg_parser.add_argument('--verbose',
                                action="store_true",
                                default=self.verbose,
                                help='Enable verbose log output. Useful for debugging.')


    def configuration(self, args=None):
        assert args

        log_level = Scaffold.LOG_LEVEL_MAP.get(self.log_level, ERROR)

        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.basicConfig(
            filename=self.name + '.log',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=log_level)
        self.log = logging.getLogger('windmills')


    def _execute_configuration(self, argv=None):
        """
        Collect the options for parsing from each service which is
        interested. This is done by invoking the configuration_options on
        each  of the base classes.

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
