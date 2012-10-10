import argparse
from cornerstone import Cornerstone


__author__ = 'neoinsanity'


class Scaffold(Cornerstone):
    """
    The Scaffold class is a helper mix-in that evaluates sys.argv into options
    settings for execution of windmill devices.
    """


    def __init__(self, **kwargs):
        Cornerstone.__init__(self)

        # if there is an argv argument, then use it to set the configuration
        if 'argv' in kwargs:
            self._execute_configuration(kwargs['argv'])


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
            raise ValueError("The argv argument is missing.")

        # if this is the command line args directly, them we need to remove the
        # first argument which is the python execution command.
        if argv[0].endswith('.py'):
            argv.pop(0)

        self._arg_parser = argparse.ArgumentParser()
        self.__invoke_method_on_bases__(func_name='configuration_options',
                                     arg_parser=self._arg_parser)
        self._args = self._arg_parser.parse_args(argv)
        #todo: raul - iterate over args attrs to set on self
        self.__invoke_method_on_bases__(func_name='configure',
                                     args=self._args)
