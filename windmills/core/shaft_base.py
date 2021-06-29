import re
import signal

import zmq.green as zmq

from .scaffold import Scaffold
from .super_core import InputSocketConfig, OutputSocketConfig

__all__ = ['ShaftBase']

__author__ = 'Raul Gonzalez'


class ShaftRunStateLayer(Scaffold):
    def __init__(self, **kwargs):
        # configure the interrupt handling
        self._stop = True
        signal.signal(signal.SIGILL, self._signal_interrupt_handler)

        Scaffold.__init__(self, **kwargs)

    @property
    def should_stop(self):
        return self._stop

    def kill(self):
        """
        This method will shut down the running loop if run() method has been
        invoked.
        """
        self._stop = True


    def _signal_interrupt_handler(self, signum, frame):
        """
        This method is registered with the signal library to ensure handling
        of system interrupts. Initialization of this method is performed
        during __init__ invocation.
        """
        self.kill()


class ShaftConnectionLayer(ShaftRunStateLayer):
    def __init__(self, **kwargs):
        ShaftRunStateLayer.__init__(self, **kwargs)

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

    def send_crate(self, delivery_key, crate):
        assert delivery_key
        assert crate

        #todo: raul -  create socket/retrieve socket for now
        sock, socket_config = self._cargos.get(delivery_key)

        #todo: raul - then send crate
        msg = crate.dump

        for cnt in range(3):
            self.log.debug('poll check on socket(%s): %s', cnt, sock)
            socks = dict(self._poll.poll())
            if socks.get(sock) == zmq.POLLOUT:
                self._send(msg, sock, socket_config)
                break

    def _send(self, msg, sock, sock_config):
        assert msg

        if not sock_config.no_block_send:
            self.log.debug('Block sending: %s', msg)
            sock.send_json([msg])
        else:
            self.log.debug('No Block sending: %s', msg)
            try:
                sock.send_json([msg], zmq.NOBLOCK)
            except zmq.ZMQError as ze:
                self.log.exception('ZMQ error detection: %s', ze)
            except Exception as e:
                self.log.exception('Unexpected exception: %s', e)

    def run_poll_loop(self, socks_handler_map, heartbeat):
        """

        :param socks_handler_map:
        :type socks_handler_map: dict
        :param heartbeat:
        :type heartbeat: int
        """
        print(('run_poll_loop: %s, %s' % (socks_handler_map, heartbeat)))
        while True:
            try:
                socks = dict(self._poll.poll(timeout=heartbeat * 1000000))
                for input_sock in list(socks_handler_map.keys()):
                    if socks.get(input_sock) == zmq.POLLIN:
                        msg = socks_handler_map[input_sock].recv_handler(
                            input_sock)

                if (self._control_sock and socks.get(
                        self._control_sock) == zmq.POLLIN):
                    msg = self._control_sock.recv()
                    self.log.info('Command msg: %s', msg)
                    if self._command_handler is not None:
                        self._command_handler(msg)
                        if self.should_stop:
                            break

                if self.should_stop:
                    self.log.info('Stop flag triggered ... shutting down.')
                    break

            except zmq.ZMQError as ze:
                if ze.errno == 4: # Known exception due to keyboard ctrl+c
                    self.log.info('System interrupt call detected.')
                else: # exit hard on unhandled exceptions
                    self.log.error(
                        'Unhandled exception in run execution:%d - %s' % (
                            ze.errno, ze.strerror))
                    exit(-1)


class ShaftBase(ShaftConnectionLayer):
    def __init__(self, **kwargs):
        ShaftConnectionLayer.__init__(self, **kwargs)
