import argparse
from random import randint
import signal
from sys import maxint

from gevent import joinall, sleep, spawn
import zmq.green as zmq

from super_core import (ConnectionManager, DeliveryHandler,
                        InputSocketConfig, OutputSocketConfig)
from super_core import DEFAULT_INPUT_OPTIONS, DEFAULT_OUTPUT_OPTIONS
from blade import Blade
from brick import Brick
from cargo import Cargo
from cornerstone import Cornerstone
from scaffold import Scaffold


__author__ = 'Raul Gonzalez'


class Shaft(Scaffold, ConnectionManager):
    def __init__(self, **kwargs):
        ConnectionManager.__init__(self)

        self._bricks = list()
        self._cornerstone = None

        # configure the interrupt handling
        self._stop = True
        signal.signal(signal.SIGILL, self._signal_interrupt_handler)

        #: a heartbeat interval that will be relaid to control channel
        self.heartbeat = 1

        # set the default handler, if name has been assigned.
        self.register_command_handler(self._default_command_handler)

        Scaffold.__init__(self, **kwargs)

    def configuration_options(self, arg_parser=argparse.ArgumentParser()):
        assert arg_parser

        arg_parser.add_argument('--heartbeat',
                                type=int,
                                default=self.heartbeat,
                                help='Set the heartbeat rate in seconds.')

    def configure(self, args=list()):
        assert args

        self.log.debug('... shaft configuration complete ...')

    def declare_blade(self, handler=None, socket_options=DEFAULT_INPUT_OPTIONS):
        """

        :param handler:
        :type handler: MethodType or FunctionType
        :param socket_options:
        :type socket_options: dict
        """
        if handler == None:
            raise ValueError('Must pass handler method to be called to accept '
                             'received Cargo object.')

        self.log.info('... Configuring socket options: %s', socket_options)

        blade_sock, socket_config = self.get_input_socket(socket_options)

        blade = Blade(handler=handler, socket_config=socket_config)
        self._blades[blade] = (blade_sock, socket_config)

        return blade

    def declare_brick(self, target, *args, **kwargs):

        self.log.info('... Configuring brick: %s, %s, %s', target, args, kwargs)

        brick = Brick(func=target, *args, **kwargs)

        self._bricks.append(brick)

    def declare_cargo(self, socket_options=DEFAULT_OUTPUT_OPTIONS):

        self.log.info('... Configuring cargo socket: %s', socket_options)


        # abstract handle to allow cargo instance to deliver a message
        delivery_key = randint(-maxint - 1, maxint)
        delivery_handler = DeliveryHandler(delivery_key=delivery_key,
                                           send_func=self.send_crate)

        cargo_sock, socket_config = self.get_output_sock(socket_options)

        cargo = Cargo(delivery_handle=delivery_handler.send_crate,
                      socket_config=socket_config)
        self._cargos[delivery_key] = (cargo_sock, socket_config)
        return cargo

    def declare_cornerstone(self, target, *args, **kwargs):
        self._cornerstone = Cornerstone(target, *args, **kwargs)

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
                self.send(msg, sock, socket_config)
                break

    def send(self, msg, sock, sock_config):
        assert msg

        if not sock_config.no_block_send:
            self.log.debug('Block sending: %s', msg)
            sock.send_multipart([msg])
        else:
            self.log.debug('No Block sending: %s', msg)
            try:
                sock.send_multipart([msg], zmq.NOBLOCK)
            except zmq.ZMQError as ze:
                self.log.exception('ZMQ error detection: %s', ze)
            except Exception as e:
                self.log.exception('Unexpected exception: %s', e)

    def is_stopped(self):
        return self._stop

    def run(self):
        self._stop = False

        self.log.info('Beginning run() with configuration: %s', self)
        # initialize the input sockets
        socks_handler_map = dict()
        for blade in self._blades.keys():
            blade_sock, socket_config = self._blades[blade]
            self.log.debug('Initialize socket: %s', socket_config)
            self._poll.register(blade_sock, zmq.POLLIN)
            socks_handler_map[blade_sock] = blade

        #todo: raul - move this section to command configuration layer
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # of course this is when a command configuration layer get's added
        controller = self._zmq_ctx.socket(zmq.SUB)
        controller.connect('tcp://localhost:54749')
        controller.setsockopt(zmq.SUBSCRIBE, '')
        self._control_sock = controller
        self._poll.register(self._control_sock, zmq.POLLIN)
        self.log.info('Configured cmd socket')
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        self.log.info('Entering run loop')

        # start all of the bricks
        for brick in self._bricks:
            brick.start()

        poller_loop_spawn = spawn(self._run_poll_loop, socks_handler_map)

        if self._cornerstone is not None:
            cornerstone_spawn = spawn(self._cornerstone.run)
            joinall([cornerstone_spawn])
            self._stop = True
        else:
            joinall([poller_loop_spawn])

        # stop the running bricks
        for brick in self._bricks:
            brick.stop()

        # close the sockets held by the poller
        self._control_sock.close()
        for sock in socks_handler_map.keys():
            sock.close()

        for sock, socket_config in self._cargos.values():
            sock.close()

        self.log.info('Run terminated for %s', self.app_name)


    def kill(self):
        """
        This method will shut down the running loop if run() method has been
        invoked.
        """
        self.log.debug('kill has been invoked.')
        self._stop = True


    def _run_poll_loop(self, socks_handler_map):

        while True:
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat * 1000))

                for input_sock in socks_handler_map.keys():
                    if socks.get(input_sock) == zmq.POLLIN:
                        msg = socks_handler_map[input_sock].recv_handler(
                            input_sock)

                if (self._control_sock and socks.get(
                        self._control_sock) == zmq.POLLIN):
                    msg = self._control_sock.recv()
                    self.log.info('Command msg: %s', msg)
                    if self._command_handler is not None:
                        self._command_handler(msg)
                        if self._stop:
                            break

                if self._stop:
                    self.log.info('Stop flag triggered ... shutting down.')
                    break

                sleep(0)  # yield to give other spawns a chance to execute

            except zmq.ZMQError, ze:
                if ze.errno == 4: # Known exception due to keyboard ctrl+c
                    self.log.info('System interrupt call detected.')
                else: # exit hard on unhandled exceptions
                    self.log.error(
                        'Unhandled exception in run execution:%d - %s' % (
                            ze.errno, ze.strerror))
                    exit(-1)


    def _signal_interrupt_handler(self, signum, frame):
        """
        This method is registered with the signal library to ensure handling
        of system interrupts. Initialization of this method is performed
        during __init__ invocation.
        """
        self.kill()


    def _default_command_handler(self, msg):
        """
        This method is the default command channel message handler. It simply
        invokes a kill flag for any message received.
        """
        self.log.debug('Got the kill command.')
        self.kill()
