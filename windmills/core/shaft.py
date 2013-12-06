import argparse
import signal
import sys

from gevent import monkey
import zmq.green as zmq

from cargo import Cargo
from blade import Blade
from scaffold import Scaffold
from windmill_core_exception import WindmillException


__author__ = 'Raul Gonzalez'

# Need to insure that gevent monkey patching for supported libraries.
monkey.patch_all()


#: Mapping for zmq_socket_types
ZMQ_INPUT_SOCKET_TYPE = {
  'pair': zmq.PAIR,
  'pull': zmq.PULL,
  'rep': zmq.REP,
  'sub': zmq.SUB,
}

ZMQ_OUTPUT_SOCKET_TYPE = {
  'pair': zmq.PAIR,
  'pub': zmq.PUB,
  'push': zmq.PUSH,
  'req': zmq.REQ,
}


class SocketConfig(object):
  def __init__(self,
               url='tcp://localhost:60053',
               sock_type='pair',
               sock_filter='',
               sock_bind=False,
               linger=0,
               monitor_stream=False,
               no_block_send=False):
    self.url = url
    self.sock_type = sock_type
    self.sock_filter = sock_filter
    self.sock_bind = sock_bind
    self.linger = linger
    self.monitor_stream = monitor_stream
    self.no_block_send = no_block_send

  def __str__(self):
    return str({
      'url': self.url,
      'sock_type': self.sock_type,
      'sock_filter': self.sock_filter,
      'sock_bind': self.sock_bind,
      'linger': self.linger,
      'monitor_stream': self.monitor_stream,
      'no_block_send': self.no_block_send,
    })


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
    self.heartbeat = 3

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

  def declare_blade(self, handler=None, socket_config=SocketConfig()):

    if handler == None:
      raise ValueError('Must pass handler method to be called to accept '
                       'received Cargo object.')

    self.log.info('... Configuring blade socket: %s', socket_config)
    blade = Blade(shaft=self, handler=handler)

    # create and store the socket
    socket_type = ZMQ_INPUT_SOCKET_TYPE[socket_config.sock_type.lower()]
    blade_sock = self._zmq_ctx.socket(socket_type)
    blade_sock.linger = socket_config.linger

    if socket_config.sock_bind:
      blade_sock.bind(socket_config.url)
    else:
      blade_sock.connect(socket_config.url)

    self._blades[blade] = (blade_sock, socket_config)

    return blade

  def declare_cargo(self,
                    handler=None,
                    socket_config=SocketConfig()):

    self.log.info('... Configuring cargo socket: %s', socket_config)
    cargo = Cargo(shaft=self, handler=handler)

    # create and store the socket
    socket_type = ZMQ_OUTPUT_SOCKET_TYPE[socket_config.sock_type.lower()]
    cargo_sock = self._zmq_ctx.socket(socket_type)
    cargo_sock.linger = socket_config.linger

    if socket_config.sock_bind:
      cargo_sock.bind(socket_config.url)
    else:
      cargo_sock.connect(socket_config.url)

    self._cargos[cargo] = (cargo_sock, socket_config)

    return cargo

  def _configure_socket(self, socket_config):
    assert socket_config

    try:
      sock_type = ZMQ_OUTPUT_SOCKET_TYPE.get(socket_config.sock_type, None)
      if sock_type is None:
        raise ValueError(
          'Unknown output socket type: %s', socket_config.sock_type)

    except zmq.ZMQError as ze:
      self.log.exception(ze)
      raise WindmillException(ze.message)
    except Exception as e:
      self.log.exception(e)
      raise WindmillException(str(e))


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
    controller = self._zmq_ctx.socket(zmq.PAIR)
    controller.connect('tcp://localhost:54749')
    # controller.setsockopt(zmq.SUBSCRIBE, '')
    self._control_sock = controller
    self._poll.register(self._control_sock, zmq.POLLIN)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    self.log.debug('Entering run loop')

    while True:
      try:
        socks = dict(self._poll.poll(timeout=self.heartbeat))

        for input_sock in socks_handler_map.keys():
          if socks.get(input_sock) == zmq.POLLIN:
            msg = socks_handler_map[input_sock].recv_handler(input_sock)

        if (self._control_sock and socks.get(
              self._control_sock) == zmq.POLLIN):
          msg = self._control_sock.recv()
          self.log.debug('Command msg: %s', msg)
          if self._command_handler is not None:
            self._command_handler(msg)

        if self._stop:
          self.log.info('Stop flag triggered ... shutting down.')
          break

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
