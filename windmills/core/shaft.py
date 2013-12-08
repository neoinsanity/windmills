import argparse
import signal
import sys

from gevent import sleep
import zmq.green as zmq

from super_core import InputSocketConfig, OutputSocketConfig
from super_core import DEFAULT_INPUT_OPTIONS, DEFAULT_OUTPUT_OPTIONS
from cargo import Cargo
from blade import Blade
from scaffold import Scaffold


__author__ = 'Raul Gonzalez'


class Shaft(Scaffold):
  def __init__(self, **kwargs):
    self._blades = dict()
    self._cargos = dict()
    self._output_sock = None
    self._control_sock = None

    # configure the interrupt handling
    self._stop = True
    signal.signal(signal.SIGILL, self._signal_interrupt_handler)

    #: a heartbeat interval that will be relaid to control channel
    self.heartbeat = 1

    # create the zmq context for
    self._zmq_ctx = zmq.Context()

    # set the default handler, if name has been assigned.
    if not hasattr(self, '_command_handler'):
      self._command_handler = self._default_command_handler

    # construct the poller
    self._poll = zmq.Poller()

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
    if handler == None:
      raise ValueError('Must pass handler method to be called to accept '
                       'received Cargo object.')

    self.log.info('... Configuring socket options: %s', socket_options)
    blade = Blade(shaft=self, handler=handler)

    # create and store the socket
    socket_config = InputSocketConfig(socket_options)
    InputSocketConfig.validate(socket_config)
    blade_sock = self._zmq_ctx.socket(socket_config.zmq_sock_type)
    blade_sock.linger = socket_config.linger

    if socket_config.sock_bind:
      if socket_config.url.endswith('*'):
        blade.port = blade_sock.bind_to_random_port(socket_config.url,
                                                    min_port=200000,
                                                    max_port=200500)
      else:
        blade_sock.bind(socket_config.url)
    else:
      blade_sock.connect(socket_config.url)

    self._blades[blade] = (blade_sock, socket_config)
    return blade

  def declare_cargo(self, callback=None, socket_options=DEFAULT_OUTPUT_OPTIONS):

    self.log.info('... Configuring cargo socket: %s', socket_options)
    cargo = Cargo(shaft=self, handler=callback)

    # create and store the socket
    socket_config = OutputSocketConfig(socket_options)
    OutputSocketConfig.validate(socket_config)
    cargo_sock = self._zmq_ctx.socket(socket_config.zmq_sock_type)
    cargo_sock.linger = socket_config.linger

    if socket_config.sock_bind:
      if socket_config.url.endswith('*'):
        cargo.port = cargo_sock.bind_to_random_port(socket_config.url,
                                                    min_port=200501,
                                                    max_port=300000)
      else:
        cargo_sock.bind(socket_config.url)
    else:
      cargo_sock.connect(socket_config.url)

    self._cargos[cargo] = (cargo_sock, socket_config)

    return cargo

  def send_crate(self, cargo, crate):
    assert crate

    #todo: raul -  create socket/retrieve socket for now
    sock, socket_config = self._cargos.get(cargo)

    #todo: raul - then send crate
    msg = crate.dump
    self.send(msg, sock, socket_config)

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
      except Exception:
        self.log.exception('Unexpected error: %s', sys.exc_info()[0])

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

    while True:
      try:
        socks = dict(self._poll.poll(timeout=self.heartbeat))

        for input_sock in socks_handler_map.keys():
          if socks.get(input_sock) == zmq.POLLIN:
            msg = socks_handler_map[input_sock].recv_handler(input_sock)

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
          self.log.error('Unhandled exception in run execution:%d - %s'
                         % (ze.errno, ze.strerror))
          exit(-1)

    # close the sockets held by the poller
    self._control_sock.close()
    for sock in socks_handler_map.keys():
      sock.close()

    for sock, socket_config in self._cargos:
      sock.close()

    self.log.info('Run terminated for %s', self.app_name)


  def kill(self):
    """
    This method will shut down the running loop if run() method has been
    invoked.
    """
    self.log.debug('kill has been invoked.')
    self._stop = True


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
