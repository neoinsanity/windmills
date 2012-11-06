"""Scaffold mix-in provides the means to add command-line configuration
options for the construction of *-windmill and app devices.
"""
import argparse
from brick import Brick


__author__ = 'neoinsanity'
__all__ = ['Scaffold']


class Scaffold(Brick):
    """
    The Scaffold class is a helper mix-in that evaluates sys.argv into options
    settings for execution of windmill devices.

    Scaffold operates by testing for the 'argv' property presence in the
    kwargs dictionary passed in the __init__ method. If the 'argv' property
    is available then, Scaffold with then call configure_options and configure
    methods that may be defined on any progenitor and ancestor base classes.

    Any classes sharing a base class chain with Scaffold will need to
    implement:
        - configure_options(self, arg_parser)
            arg_parser - is an argparse.ArgumentParser object that is used by
            each implementing base class to declare configuretion options.
        = configure(self, args)
            args - is a property object that will be set with the keyword
            value results from parsing the configuration options.

    Of note is that Scaffold will cause the application to exit if the '-h'
    or '--help' configure arguments are one of the options. In addition to
    exiting, the child class will display the command line help message.
    """


    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)

        # if there is an argv argument, then use it to set the configuration
        if 'argv' in kwargs and kwargs.get('argv') is not None:
            self._execute_configuration(kwargs['argv'])
        else:
            empty_args = self.__create_property_bag__()
            self.__invoke_method_on_bases__(func_name='configure',
                                            args=empty_args)


    def _execute_configuration(self, argv=None):
        """
        Collect the options for parsing from each service which is
        interested. This is done by invoking the configuration_options on
        each  of the base classes.

        >>> foo = Scaffold()
        >>> argv = [
        ... '/Users/neoinsanity/samples/samples/my-argparse/simpe_argparse.py',
        ... '--heartbeat', '5']
        >>> foo._execute_configuration(argv=argv)
        >>> assert foo.heartbeat == 5

        """
        if argv is None:
            argv = [] # just create an empty arg list

        arg_parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        # if this is the command line args directly, them we need to remove the
        # first argument which is the python execution command. it is
        if len(argv) > 0 and argv[0].endswith('.py'):
            argv.pop(0)

        self.__invoke_method_on_bases__(func_name='configuration_options',
                                        arg_parser=arg_parser)
        self._args = arg_parser.parse_args(argv)
        #todo: raul - iterate over args attrs to set on self
        self.__invoke_method_on_bases__(func_name='configure',
                                        args=self._args)
