#!/usr/bin/env python
from lib import Scaffold
import sys
from zmq import PULL, PUSH


__author__ = 'neoinsanity'
#
# ventilator-windmill()
#

class VentilatorWindmill(Scaffold):
    """
    >>> from threading import Thread
    >>> import time
    >>> arg_list = ['--verbose']
    >>> foo = VentilatorWindmill(argv=arg_list)
    >>> t = Thread(target=foo.run)
    >>> t.start() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Beginning run() with state: <ventilator-windmill.VentilatorWindmill
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
        self.input_sock_url = 'tcp://localhost:6677'
        self.output_sock_url = 'tcp://*:6678'

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--input_sock_url',
                                default=self.input_sock_url,
                                help='The url that the ventilator will '
                                     'connect and pull messages.')
        arg_parser.add_argument('--output_sock_url',
                                default=self.output_sock_url,
                                help='The url that the ventilator will bind '
                                     'and push messages.')


    def configure(self, args=None):
        assert args
        self.input_sock_url = args.input_sock_url
        self.output_sock_url = args.output_sock_url

        pull_socket = self.zmq_ctx.socket(PULL)
        pull_socket.connect(self.input_sock_url)
        self.register_input_sock(pull_socket)

        push_socket = self.zmq_ctx.socket(PUSH)
        push_socket.bind(self.output_sock_url)
        self.register_output_sock(push_socket)




if __name__ == '__main__':
    argv = sys.argv
    ventilator_windmill = VentilatorWindmill(argv=argv)
    ventilator_windmill.run()