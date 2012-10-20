#!/usr/bin/env python
from lib import Scaffold
from zmq import REP


__author__ = 'neoinsanity'
__all__ = ['EchoService']
#
# echo-windmill
#

class EchoService(Scaffold):
    """

    """


    def __init__(self, **kwargs):
        # setup the initial default settings
        self.reply_sock_url = 'tcp://localhost:8889'
        self.message = None

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--reply_sock_url',
                                default=self.reply_sock_url,
                                help='The url that the echo server will '
                                     'listen to')
        arg_parser.add_argument('-m', '--message',
                                default=self.message,
                                help='Optional argument. When used, '
                                     'the message argument will be echoed '
                                     'back to the requesting client. If no '
                                     'present, then echo will just echo the '
                                     'request message.')


    def configure(self, args=None):
        assert args
        property_list = ['reply_sock_url', 'message']

        reply_sock = self.zmq_ctx.socket(REP)
        reply_sock.connect(self.reply_sock_url)
