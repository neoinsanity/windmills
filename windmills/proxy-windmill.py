#!/usr/bin/env python
from lib import Scaffold
import sys
from zmq import Context, PUB, RCVMORE, SNDMORE, SUB, SUBSCRIBE


__author__ = 'neoinsanity'
#
# proxy-windmill
#

class ProxyWindmill(Scaffold):
    """
    >>> from threading import Thread
    >>> import time
    >>> arg_list = ['--verbose']
    >>> foo = ProxyWindmill(argv=arg_list)
    >>> t = Thread(target=foo.run)
    >>> t.start() # doctest: +ELLIPSIS
    Beginning run() with state: <proxy-windmill.ProxyWindmill object at ...>
    >>> time.sleep(3)
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(1)
    Stop flag triggered ... shutting down.
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        # set up the initial default settings
        self.input_sock_url = 'tcp://localhost:6667'
        self.input_sock_filter = ''
        self.output_sock_url = 'tcp://*:6668'

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--input_sock_url',
                                default=self.input_sock_url,
                                help='The url that the proxy will subscribe '
                                     'for messages.')
        arg_parser.add_argument('--input_sock_filter',
                                default=self.input_sock_filter,
                                help="This will set a 0mq filter subscription"
                                     " input.")
        arg_parser.add_argument('--output_sock_url',
                                default=self.output_sock_url,
                                help='The url that the proxy will publish '
                                     'messages upon.')


    def configure(self, args=None):
        assert args
        self.input_sock_url = args.input_sock_url
        self.output_sock_url = args.output_sock_url

        sub_socket = self.zmq_ctx.socket(SUB)
        sub_socket.connect(self.input_sock_url)
        sub_socket.setsockopt(SUBSCRIBE, self.input_sock_filter)
        self.register_input_sock(sub_socket)

        sub_socket = self.zmq_ctx.socket(PUB)
        sub_socket.bind(self.output_sock_url)
        self.register_output_sock(sub_socket)

        if self.verbose:
            print 'ProxyWindmill configured...'


if __name__ == "__main__":
    argv = sys.argv
    proxy_windmill = ProxyWindmill(argv=argv)
    proxy_windmill.run()
