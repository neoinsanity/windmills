#!/usr/bin/env python
from lib import Scaffold
import sys
import time
from zmq import PUSH


__author__ = 'neoinsanity'
#
# cli-emitter
#

class CliEmitter(Scaffold):
    """
    >>> from threading import Thread
    >>> import time
    >>> from zmq import PULL
    >>> arg_list = ['--verbose', '--output_sock_url', 'tcp://*:9999']
    >>> foo = CliEmitter(argv=arg_list)
    >>> input_sock = foo.zmq_ctx.socket(PULL)
    >>> input_sock.connect('tcp://localhost:9999')
    >>> foo.run()
    >>> msg = input_sock.recv()
    >>> print msg
    Testing 1, 2, 3
    """


    def __init__(self, **kwargs):
        # setup the initial default configuration
        self.output_sock_url = "tcp://*:6677"
        self.delay = 1
        self.file = None
        self.message = 'Testing 1, 2, 3'
        self.repeat = False

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--output_sock_url',
                                default=self.output_sock_url,
                                help='The url that emitter will bind and push'
                                     ' messages')
        arg_parser.add_argument('-d', '--delay',
                                type=int,
                                default=self.delay,
                                help='The delay in the transmission of '
                                     'multi-line file or repeat messages. A '
                                     '0 delay will disable any delay, '
                                     'A negative delay value is not allowed.')
        arg_parser.add_argument('-f', '--file',
                                default=self.file,
                                help='Use of this flag will cause cli-emitter'
                                     ' to transmit each line of a given file.'
                                     ' Use of this argument will cause '
                                     '-m|--message argument to be ignored.')
        arg_parser.add_argument('-m', '--message',
                                default=self.message,
                                help="The message that the emitter will send "
                                     "on the output sockeet. If the -f|--file"
                                     " flag is used, then this message flag "
                                     "is ignored.")
        arg_parser.add_argument('-r', '--repeat',
                                default=self.repeat,
                                action='store_true',
                                help='This flag will cause cli-emitter to '
                                     'repeat transmission of messages. In the'
                                     ' case of a file, cli-emitter will loop '
                                     'through the contents of the file.')


    def configure(self, args=None):
        """
        >>> foo = CliEmitter()
        >>> args = foo.__create_property_bag__()
        >>> args.output_sock_url = 'tcp://*:9998'
        >>> args.delay = 5
        >>> args.file = '/User/local/someone/somefile'
        >>> args.message = 'Welcome to my world'
        >>> args.repeat = True
        >>> foo.configure(args=args)
        >>> assert foo.output_sock_url == args.output_sock_url
        >>> assert foo.delay == args.delay
        >>> assert foo.file == args.file
        >>> assert foo.message == args.message
        >>> assert foo.repeat == args.repeat
        """
        assert args
        property_list = ['output_sock_url', 'delay', 'file', 'message',
                         'repeat']
        self.__copy_property_values__(src=args,
                                      target=self,
                                      property_list=property_list)

        push_socket = self.zmq_ctx.socket(PUSH)
        push_socket.bind(self.output_sock_url)
        self.register_output_sock(push_socket)

        if self.verbose:
            print 'CliEmitter configured...'


    def run(self):
        """

        """

        if self.file is None:
            send_method = self._send_msg
        else:
            send_method = self._send_file

        if not self.repeat:
            send_method()
        else:
            # todo: raul - need better way to do stop notification
            while(not self.isStopped()):
                send_method()

        # give it time to die.
        time.sleep(1)


    def _send_file(self):
        with open(self.file, 'r') as f:
            for msg in f:
                self._transmit(msg)
                if(self.isStopped()):
                    break


    def _send_msg(self):
        self._transmit(self.message)


    def _transmit(self, msg):
        if self.delay > 0:
            time.sleep(self.delay)

        self.send(msg)


if __name__ == '__main__':
    argv = sys.argv
    cli_emitter = CliEmitter(argv=argv)
    cli_emitter.run()
