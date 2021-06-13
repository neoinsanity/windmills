from windmills.core import Shaft

__author__ = 'Raul Gonzalez'


class EchoService(Shaft):
    def __init__(self, **kwargs):
        self.message = None

        Shaft.__init__(self, **kwargs)

    def configuration_options(self, arg_parser=None):
        """

        :param arg_parser:
        :type arg_parser: argparse.ArgumentParser
        :return:
        """
        assert arg_parser

        arg_parser.add_argument('-m', '--message',
                                default=self.message,
                                help='Optional argument. When used, '
                                     'the message argument will be echoed '
                                     'back to the requesting client. If not '
                                     'present, then echo will just echo the '
                                     'request message.')

    def configure(self, args=None):
        """

        :param args:
        :type args: list
        :return:
        """
        assert args

    def echo_rec_handler(self, input_sock):
        msg = input_sock.recv_multipart()

        self.log.debug('echoing: %s', msg)

        if self.message is None:
            input_sock.send_multipart(msg)
            return msg
        else:
            input_sock.send_multipart([self.message])
            return self.message
