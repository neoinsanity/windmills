#!/usr/bin/env python
from lib import Brick
import sys


__author__ = 'neoinsanity'
__all__ = ['VentilatorWindmill']
#
# ventilator-windmill()
#

class VentilatorWindmill(Brick):
    """
    >>> from threading import Thread
    >>> import time
    >>> arg_list = ['--verbose']
    >>> foo = VentilatorWindmill(argv=arg_list)
    >>> t = Thread(target=foo.run)
    >>> t.start() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Beginning run() with state: <ventilator_windmill.VentilatorWindmill
    object at ...>
    >>> time.sleep(3)
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(1)
    Stop flag triggered ... shutting down.
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        # set up the initial default configuration
        self.input_sock_url = 'tcp://localhost:6687'
        self.input_sock_type = "PULL"

        self.output_sock_url = 'tcp://*:6688'
        self.output_sock_type = "PUSH"

        Brick.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser


    def configure(self, args=None):
        assert args

        self.log.info('Ventilator Windmill configured ...')


if __name__ == '__main__':
    argv = sys.argv
    ventilator_windmill = VentilatorWindmill(argv=argv)
    ventilator_windmill.run()
