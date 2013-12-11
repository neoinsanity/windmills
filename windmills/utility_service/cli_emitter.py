import sys
import time
from windmills.core import Crate, Shaft

__author__ = 'Raul Gonzalez'


class CliEmitter(Shaft):
    def __init__(self, **kwargs):
        self.delay = 0
        self.file = None
        self.message = 'Hello World'
        self.repeat = False

        Shaft.__init__(self, **kwargs)

        self.cargo = self.declare_cargo()
        self.declare_cornerstone(self.run_loop)

    def configuration_options(self, arg_parser=None):
        assert arg_parser

        arg_parser.add_argument('-d', '--delay',
                                type=int,
                                default=self.delay,
                                help='The delay in in seconds for transmission of '
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
                                type=str,
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

    def configure(self, args=list()):
        assert args

        self.log.info('CliEmitter configured ...')


    def run_loop(self):
        """

        """
        try:
            self._stop = False  #TODO: raul - need to remove this for call back

            if self.file is None:
                send_method = self._send_msg
            else:
                send_method = self._send_file

            if not self.repeat:
                send_method()
            else:
                # todo: raul - need better way to do stop notification
                while not self.is_stopped():
                    send_method()

            # give it time to die.
            time.sleep(1)
        except Exception as e:
            self.log.exception('Unknown Exception: %s', e)
            raise e
        finally:
            self.kill()
            self.log.info('CliEmitter shutting down.')


    def _send_file(self):
        with open(self.file, 'r') as f:
            for msg in f:
                self._transmit(msg.rstrip())
                if self.is_stopped():
                    return


    def _send_msg(self):
        self._transmit(self.message)


    def _transmit(self, msg):
        if self.delay > 0:
            time.sleep(self.delay)

        self.log.debug('transmit msg: %s', msg)
        crate = Crate(msg_data=msg)
        self.cargo.send(crate)


if __name__ == '__main__':
    argv = sys.argv
    cli_emitter = CliEmitter(argv=argv)
    cli_emitter.run()
