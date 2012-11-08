"""Brick is a mix-in that contains functionality to configure input and
output sockets for 0mq device and service patterns.
"""
from cornerstone import Cornerstone
from zmq import PULL, PUSH, SUB, SUBSCRIBE


__author__ = 'neoinsanity'
__all__ = ['Brick']


class Brick(Cornerstone):
    def __init__(self, **kwargs):
        """
        >>> foo = Brick()
        >>> assert foo.output_sock_url == 'tcp://*:6677'
        >>> assert foo.output_sock_type == 'PUSH'
        >>> # Need to shut off the sockets
        >>> foo.register_input_sock(sock = None)
        >>> foo.register_output_sock(sock = None)
        """
        # The list of attributes that should be set if input handling is required
        if not hasattr(self, 'CONFIGURE_INPUT'):
            self.CONFIGURE_INPUT = True

        if self.CONFIGURE_INPUT:
            input_attr_list = [
                ('input_sock_url', 'tcp://localhost:6678'),
                ('input_sock_type', 'PULL'),
                ('input_sock_filter', '')
            ]
            self.__set_unassigned_attrs__(self, input_attr_list)

        # The list of attributes that should be set if input handling is required
        if not hasattr(self, 'CONFIGURE_OUTPUT'):
            self.CONFIGURE_OUTPUT = True

        if self.CONFIGURE_OUTPUT:
            output_attr_list = [
                ('output_sock_url', 'tcp://*:6677'),
                ('output_sock_type', 'PUSH')
            ]
            self.__set_unassigned_attrs__(self, output_attr_list)

        Cornerstone.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser

        # input configuration options
        if self.CONFIGURE_INPUT:
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

        # output configuration options
        if self.CONFIGURE_OUTPUT:
            arg_parser.add_argument('--output_sock_url',
                                    default=self.output_sock_url,
                                    help='The url that emitter will bind and push'
                                         ' messages')


    def configure(self, args=None):
        assert args

        if self.CONFIGURE_INPUT:
            sock_type = PULL
            if self.input_sock_type == 'SUB':
                sock_type = SUB
            pull_socket = self.zmq_ctx.socket(sock_type)
            if sock_type == SUB:
                pull_socket.setsockopt(SUBSCRIBE, self.input_sock_filter)

            pull_socket.connect(self.input_sock_url)
            self.register_input_sock(pull_socket)

        if self.CONFIGURE_OUTPUT:
            push_socket = self.zmq_ctx.socket(PUSH)
            push_socket.bind(self.output_sock_url)
            self.register_output_sock(push_socket)
