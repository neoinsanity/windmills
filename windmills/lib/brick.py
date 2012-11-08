"""Brick is a mix-in that contains functionality to configure input and
output sockets for 0mq device and service patterns.
"""
from cornerstone import Cornerstone
from zmq import PUSH


__author__ = 'neoinsanity'
__all__ = ['Brick']


class Brick(Cornerstone):
    """

    """


    def __init__(self, **kwargs):
        """
        >>> foo = Brick()
        >>> assert foo.output_sock_url == 'tcp://*:6677'
        >>> assert foo.output_sock_type == 'PUSH'
        >>> # Need to shut off the socket
        >>> foo.register_output_sock(sock = None)
        """
        # The list of attributes that are used by Brick
        attr_list = [
            ['output_sock_url', 'tcp://*:6677'],
            ['output_sock_type', 'PUSH']
        ]
        self.__set_attrs__(self, attr_list)

        Cornerstone.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--output_sock_url',
                                default=self.output_sock_url,
                                help='The url that emitter will bind and push'
                                     ' messages')


    def configure(self, args=None):
        assert args

        push_socket = self.zmq_ctx.socket(PUSH)
        push_socket.bind(self.output_sock_url)
        self.register_output_sock(push_socket)
