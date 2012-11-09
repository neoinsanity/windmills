#!/usr/bin/env python
from lib import Cornerstone
from zmq import   REP


__author__ = 'neoinsanity'
__all__ = ['EchoService']
#
# echo-windmill
#

class EchoService(Cornerstone):
    """
    >>> from threading import Thread
    >>> import time
    >>> arg_list = ['--verbose']
    >>> foo = EchoService(argv=arg_list)
    >>> t = Thread(target=foo.run)
    >>> t.start() # doctest: +ELLIPSIS
    Beginning run() with state: <...EchoService object at ...> and configuration:  Namespace(heartbeat=3, message=None, monitor_stream=False, no_block_send=False, reply_sock_url='tcp://localhost:8889', verbose=True)
    >>> time.sleep(1)
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(1)
    Stop flag triggered ... shutting down.
    Shut down EchoService ...
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        # setup the initial default settings
        self.reply_sock_url = 'tcp://localhost:8889'
        self.message = None

        # todo: raul - this is cheesy, and needs to be replaced with a more
        # elegant method of setting the handler.
        self.input_recv_handler = self._echo_rec_handler

        Cornerstone.__init__(self, **kwargs)


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

        reply_sock = self.zmq_ctx.socket(REP)
        reply_sock.connect(self.reply_sock_url)

        self.register_input_sock(reply_sock)
        self.register_output_sock(reply_sock)


    def _echo_rec_handler(self, input_sock):
        msg = input_sock.recv()

        if self.message is None:
            self._output_sock.send(msg)
            return msg

        else:
            self._output_sock.send(self.message)
            return self.message
