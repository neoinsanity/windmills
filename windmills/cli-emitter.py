#!/usr/bin/env python
from scaffold import Scaffold
import sys


__author__ = 'neoinsanity'
#
# cli-emitter
#

class CliEmitter(Scaffold):
    """
    >>> from threading import Thread
    >>> import time
    >>> arg_list = ['--verbose']
    >>> foo = CliEmitter(argv=arg_list)
    >>> t = Thread(target=foo.run)
    >>> t.start() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    >>> time.sleep(3)
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(1)
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        # setup the initial default configuration
        self.output_sock_url = "tcp://*.6677"

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--output_sock_url',
                                default=self.output_sock_url,
                                help='The url that emitter will bind and push'
                                     ' messages')
        arg_parser.add_argument('-d', '--delay',
                                type=int,
                                default=3,
                                help='The delay in the transmission of '
                                     'multi-line file or repeat messages.')
        arg_parser.add_argument('-f', '--file',
                                help='Use of this flag will cause cli-emitter'
                                     ' to transmit each line of a given file.'
                                     ' Use of this argument will cause '
                                     '-m|--message argument to be ignored.')
        arg_parser.add_argument('-m', '--message',
                                default='Testing 1 2 3',
                                help="The message that the emitter will send "
                                     "on the output sockeet. If the -f|--file"
                                     " flag is used, then this message flag "
                                     "is ignored.")
        arg_parser.add_argument('-r', '--repeat',
                                action='store_true',
                                help='This flag will cause cli-emitter to '
                                     'repeat transmission of messages. In the'
                                     ' case of a file, cli-emitter will loop '
                                     'through the contents of the file.')


    def configure(self, args=None):
        assert args


    def run(self):
        """

        """
        pass

if __name__ == '__main__':
    argv = sys.argv
    cli_emitter = CliEmitter(argv=argv)
    cli_emitter.run()
