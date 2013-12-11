import re

import zmq.green as zmq

from socket_config import InputSocketConfig, OutputSocketConfig

__author__ = 'Raul Gonzalez'


class ConnectionManager(object):
    def __init__(self):
        self._blades = dict()
        self._cargos = dict()
        self._control_sock = None
        self._command_handler = None

        self._zmq_ctx = zmq.Context()
        self._poll = zmq.Poller()

    def register_command_handler(self, command_handler=None):
        """

        :param command_handler:
        :type command_handler: MethodType or FunctionType
        """
        assert command_handler
        self._command_handler = command_handler

    def get_input_socket(self, socket_options):
        """

        :param socket_options:
        :return:
        :rtype: zmq.Socket, InputSocketConfig
        """

        socket_config = InputSocketConfig(socket_options)
        InputSocketConfig.validate(socket_config)

        input_sock = self._zmq_ctx.socket(socket_config.zmq_sock_type)
        input_sock.linger = socket_config.linger

        port = None
        if socket_config.sock_bind:
            if socket_config.url.endswith('*'):
                port = input_sock.bind_to_random_port(socket_config.url,
                                                      min_port=200000,
                                                      max_port=250000)
            else:
                input_sock.bind(socket_config.url)
        else:
            input_sock.connect(socket_config.url)

        # actual creation and recording of Cargo
        if not port:
            port = re.match('.*?([0-9]+)$', socket_config.url).group(1)

        socket_config.port = port

        return input_sock, socket_config

    def get_output_sock(self, socket_options):
        """

        :param socket_options:
        :type socket_options: dict
        :return:
        :rtype: zmq.Socket, OutputSocketConfig
        """
        # create and store the socket
        socket_config = OutputSocketConfig(socket_options)
        OutputSocketConfig.validate(socket_config)
        output_sock = self._zmq_ctx.socket(socket_config.zmq_sock_type)
        output_sock.linger = socket_config.linger

        port = None
        if socket_config.sock_bind:
            if socket_config.url.endswith('*'):
                port = output_sock.bind_to_random_port(socket_config.url,
                                                       min_port=200501,
                                                       max_port=300000)
            else:
                output_sock.bind(socket_config.url)
        else:
            output_sock.connect(socket_config.url)

        # ensure the socket can be used for sending
        self._poll.register(output_sock, zmq.POLLOUT)

        # actual creation and recording of Cargo
        if not port:
            port = re.match('.*?([0-9]+)$', socket_config.url).group(1)

        socket_config.port = port

        return output_sock, socket_config
