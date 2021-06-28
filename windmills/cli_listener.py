#!/usr/bin/env python
from .lib import Brick
import sys


__author__ = 'neoinsanity'
__all__ = ['CliListener']
#
# cli-listener
#

class CliListener(Brick):
    """
    >>> from threading import Thread
    >>> import time
    >>> arg_list = ['--verbose']
    >>> foo = CliListener(argv=arg_list)
    CliListener configured...
    >>> t = Thread(target=foo.run)
    >>> t.start() # doctest: +ELLIPSIS
    Beginning run() with state: <cli_listener.CliListener object at ...>
    >>> time.sleep(1)
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(1)
    Stop flag triggered ... shutting down.
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        # setup the initial default configuration
        self.file = None

        # todo: raul - this is cheesy, and needs to be replaced with a more
        # elegant method of setting the handler.
        self.input_recv_handler = self._listener_recv_handler

        self.CONFIGURE_OUTPUT = False # Signal Brick not to configure output socket
        Brick.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('-f', '--file',
                                help='A file to append incoming messages by '
                                     'line.')


    def configure(self, args=None):
        assert args

        if self.file is not None:
            self._file = open(self.file, 'w')

        self.log.info('CliListener configured...')


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

        return msg


if __name__ == '__main__':
    argv = sys.argv
    cli_listener = CliListener(argv=argv)
    cli_listener.run()
