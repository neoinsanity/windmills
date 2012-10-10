#!/usr/bin/env python
from scaffold import Scaffold
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
    >>> from zmq import Context, SUB, SUBSCRIBE
    >>> foo = ProxyWindmill()
    Proxy Windmill Initialized ...
    >>> t = Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(3)
    >>> foo.kill()
    >>> t.join(3)
    Stop flag triggered ... shutting down.
    """


    def __init__(self, **kwargs):
        Scaffold.__init__(self)

        self.input_sock_url = 'tcp://localhost:6667'
        self.input_sock_filter = ''
        self.output_sock_url = 'tcp://*:6668'

        print 'Proxy Windmill Initialized ...'


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

        server_sock = self.zmq_ctx.socket(SUB)
        server_sock.connect(self.input_sock_url)
        server_sock.setsockopt(SUBSCRIBE, self.input_sock_filter)
        self.register_input_sock(server_sock)

        client_sock = self.zmq_ctx.socket(PUB)
        client_sock.bind(self.output_sock_url)
        self.register_output_sock(client_sock)

        controller = self.zmq_ctx.socket(SUB)
        controller.connect('tcp://localhost:7885')
        controller.setsockopt(SUBSCRIBE, "")
        self._control_sock = controller


if __name__ == "__main__":
    argv = sys.argv
    proxyWindmill = ProxyWindmill(argv=argv)
    proxyWindmill.run()
