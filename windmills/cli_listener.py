#!/usr/bin/env python
from lib import Scaffold
import sys
from zmq import PULL, SUB, SUBSCRIBE


__author__ = 'neoinsanity'
__all__ = ['CliListener']
#
# cli-listener
#

class CliListener(Scaffold):
    """
    >>> from threading import Thread
    >>> import time
    >>> arg_list = ['--verbose']
    >>> foo = CliListener(argv=arg_list)
    >>> t = Thread(target=foo.run)
    >>> t.start() # doctest: +ELLIPSIS
    Beginning run() with state: <cli_listener.CliListener object at ...>
    >>> time.sleep(3)
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(1)
    Stop flag triggered ... shutting down.
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        # setup the initial default configuration
        self.input_sock_url = "tcp://localhost:6678"
        self.input_sock_type = 'PULL'
        self.input_sock_filter = ""
        self.file = None

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--input_sock_url',
                                default=self.input_sock_url,
                                help='The url that the listener will pull '
                                     'from to print out messages')
        arg_parser.add_argument('--input_sock_type',
                                default=self.input_sock_type,
                                help='The type of socket to create. ('
                                     'PULL|SUB)')
        arg_parser.add_argument('--input_sock_filter',
                                default=self.input_sock_filter,
                                help='The filter argument is only valid if '
                                     'the input_sock_type is set to SUB.')
        arg_parser.add_argument('-f', '--file',
                                help='A file to append incoming messages by '
                                     'line.')


    def configure(self, args=None):
        assert args
        property_list = ['input_sock_url', 'file']
        self.__copy_property_values__(src=args,
                                      target=self,
                                      property_list=property_list)

        if self.file is not None:
            self._file = open(self.file, 'w')

        sock_type = PULL
        if self.input_sock_type == 'SUB':
            sock_type = SUB
        pull_socket = self.zmq_ctx.socket(sock_type)
        if sock_type == SUB:
            pull_socket.setsockopt(SUBSCRIBE, self.input_sock_filter)

        pull_socket.connect(self.input_sock_url)
        self.register_input_sock(pull_socket)

        #todo: raul - find a better way to do socket.recv handling registring
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # self._input_recv_handler is defined in the Cornerstone class.
        #Override with out own listener
        args.recv = '_listener_recv_handler'

        #self._input_recv_handler = self._listener_recv_handler
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        if self.verbose:
            print 'CliListener configured...'


    def _listener_recv_handler(self, sock):
        """
        This method is a replacement for Cornerstone._default_recv_handler.
        It will take an incoming input message and display it to console,
        or it will send the incoming message content to a designated file is
        one is provided.
        """
        msg = self._input_sock.recv()

        if(self.file is None):
            sys.stdout.write(msg)
            sys.stdout.flush()
        else:
            self._file.write(msg)
            self._file.flush()


if __name__ == '__main__':
    argv = sys.argv
    cli_listener = CliListener(argv=argv)
    cli_listener.run()
