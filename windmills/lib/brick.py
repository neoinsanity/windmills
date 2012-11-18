"""Brick is a mix-in that contains functionality to configure input and
output sockets for 0mq device and service patterns.
"""
from cornerstone import Cornerstone
from zmq import PUB, PULL, PUSH, SUB, SUBSCRIBE


__author__ = 'neoinsanity'
__all__ = ['Brick']


class Brick(Cornerstone):
    def __init__(self, **kwargs):
        """
        >>> foo = Brick()
        >>> assert foo.input_sock_url == 'tcp://localhost:6678'
        >>> assert foo.input_sock_type == 'PULL'
        >>> assert foo.input_sock_filter == ''
        >>> assert foo.input_bind == False
        >>> assert foo.output_sock_url == 'tcp://*:6677'
        >>> assert foo.output_sock_type == 'PUSH'
        >>> assert foo.output_connect == False
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
                ('input_sock_filter', ''),
                ('input_bind', False)
            ]
            self.__set_unassigned_attrs__(self, input_attr_list)

        # The list of attributes that should be set if input handling is required
        if not hasattr(self, 'CONFIGURE_OUTPUT'):
            self.CONFIGURE_OUTPUT = True

        if self.CONFIGURE_OUTPUT:
            output_attr_list = [
                ('output_sock_url', 'tcp://*:6677'),
                ('output_sock_type', 'PUSH'),
                ('output_connect', False)
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
                                    help='The type of socket to create. (PULL|SUB)')
            arg_parser.add_argument('--input_sock_filter',
                                    default=self.input_sock_filter,
                                    help='The filter argument is only valid if '
                                         'the input_sock_type is set to SUB.')
            arg_parser.add_argument('--input_bind',
                                    default=self.input_bind,
                                    action='store_true',
                                    help='Configure the input to bind rather '
                                         'than connect on the input url')
            arg_parser.add_argument('--input_connect',
                                    dest='input_bind',
                                    action='store_false',
                                    help='Configure the input to connect rather '
                                         'than bind on the input url')


        # output configuration options
        if self.CONFIGURE_OUTPUT:
            arg_parser.add_argument('--output_sock_url',
                                    default=self.output_sock_url,
                                    help='The url that emitter will bind and push'
                                         ' messages')
            arg_parser.add_argument('--output_sock_type',
                                    default=self.output_sock_type,
                                    help='The type of socket to create, (PUSH|PUB')
            arg_parser.add_argument('--output_connect',
                                    default=self.output_connect,
                                    action='store_true',
                                    help='Configure the output to connect rather '
                                         'than bind on the output url')
            arg_parser.add_argument('--output_bind',
                                    dest='output_connect',
                                    action='store_false',
                                    help='Configure the output to bind rather '
                                         'then connect on the output url')


    def configure(self, args=None):
        assert args

        # configure input socket to include the socket option settings
        if self.CONFIGURE_INPUT:
            sock_type = PULL
            if self.input_sock_type == 'SUB':
                sock_type = SUB
            input_socket = self.zmq_ctx.socket(sock_type)

            # set the input options
            if sock_type == SUB:
                input_socket.setsockopt(SUBSCRIBE, self.input_sock_filter)

            if  self.input_bind:
                input_socket.bind(self.input_sock_url)
            else:
                input_socket.connect(self.input_sock_url)
            self.register_input_sock(input_socket)

        # configure output socket to include the socket option settings
        if self.CONFIGURE_OUTPUT:
            sock_type = PUSH
            if self.output_sock_type == 'PUB':
                sock_type = PUB
            output_socket = self.zmq_ctx.socket(sock_type)

            if self.output_connect:
                output_socket.connect(self.output_sock_url)
            else:
                output_socket.bind(self.output_sock_url)
            self.register_output_sock(output_socket)
