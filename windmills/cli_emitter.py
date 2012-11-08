#!/usr/bin/env python
from lib import Brick
import sys
import time
from zmq import PUSH

# todo: raul - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# todo: raul - This CliEmitter does not have a complete socket configuration
# Make sure you fix this. Don't do it by just hacking into a generalize
# socket generation, then I start talking gibberish - but you get the idea.
# todo: raul - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

__author__ = 'neoinsanity'
__all__ = ['CliEmitter']
#
# cli-emitter
#

class CliEmitter(Brick):
    """
    >>> from threading import Thread
    >>> import time
    >>> from zmq import PULL
    >>> arg_list = ['--verbose', '--output_sock_url', 'tcp://*:9998']
    >>> foo = CliEmitter(argv=arg_list)
    CliEmitter configured...
    >>> input_sock = foo.zmq_ctx.socket(PULL)
    >>> input_sock.connect('tcp://localhost:9999')
    >>> foo.run()
    >>> msg = input_sock.recv()
    >>> input_sock.close()
    >>> print msg
    Testing 1, 2, 3
    """


    def __init__(self, **kwargs):
        # setup the initial default configuration
        self.output_sock_url = "tcp://*:6677"
        self.output_sock_type = 'PUSH'
        self.delay = 1
        self.file = None
        self.message = 'Testing 1, 2, 3'
        self.repeat = False

        Brick.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
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
                                     "on the output socket. If the -f|--file"
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
        assert args

        if self.verbose:
            print 'CliEmitter configured...'


    def run(self):
        """

        """

        try:
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
        except Exception, e:
            print 'Unknown Exception: ', e
            raise e
        finally:
            self.register_output_sock(None) # close the socket use


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
