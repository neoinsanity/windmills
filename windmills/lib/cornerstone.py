"""Cornerstone provides a 0mq core that consists of an input, output,
and control socket.

Configuration options provided by the Cornerstone class.
    optional arguments:
        --heartbeat HEARTBEAT
            Set the heartbeat rete in seconds of the core 0mq poller.
        --monitor_stream
            Enable the sampling of message flow.
        --verbose
            Enable verbose log output. Useful for debugging.
"""
from logging import INFO
from scaffold import Scaffold
import signal
import sys
from zmq import (Context, NOBLOCK, Poller, POLLIN, RCVMORE, SNDMORE,
                 SUB, SUBSCRIBE, ZMQError)


__author__ = 'neoinsanity'
__all__ = ['Cornerstone']


class Cornerstone(Scaffold):
    """ Cornerstone can be used to create a 0mq poll loop.

    Upon creation of a Cornerstone instance, the initial state of the instance
    internal xmq poll loop is passive. To start the loop call Cornerstone
    run(). To stop the Cornerstone instance call Cornerstone.kill().

    Cornerstone only allows for one zmq input port and one zmq output port.
    Cornerstone support respectively; Cornerstone.register_input_sock() and
    Cornerstone.register_output_sock() methods.

    Cornerstone implements an internal signal handler for detection of
    interrupt signals to handle shutdown of connection resources.

    Example Usage:
    >>> import threading
    >>> import time
    >>> from zmq import Context, SUB, SUBSCRIBE

    >>> # create, configure, and run a Cornerstone instance
    >>> foo = Cornerstone()
    >>> property_bag = foo.__create_property_bag__()
    >>> property_bag.heartbeat = 1
    >>> foo.configure(args=property_bag)
    >>> t = threading.Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(1)
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(1)
    >>> assert not t.is_alive()

    >>> # register an input socket
    >>> ctx = foo.zmq_ctx
    >>> sock = ctx.socket(SUB)
    >>> sock.connect('tcp://localhost:6670')
    >>> sock.setsockopt(SUBSCRIBE, "")
    >>> foo.register_input_sock(sock)
    >>> t = threading.Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(1)
    >>> foo.kill()
    >>> t.join(1)
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        self._input_sock = None
        self._output_sock = None
        self._control_sock = None

        # determine if outgoing messages should enable NOBLOCK on send
        # default behaviour is to block on a send call till receiver is present
        self.no_block_send = False

        # configure the interrupt handling
        self._stop = True
        signal.signal(signal.SIGINT, self._signal_interrupt_handler)

        # a regular hearbeat interval must be set to the default.
        self.heartbeat = 3 # seconds

        # create the zmq context
        self.zmq_ctx = Context()

        # set the default input receive handler, if none has been assigned
        if not hasattr(self, 'input_recv_handler'):
            self.input_recv_handler = self._default_recv_handler

        # set the default handler, if none has been assigned.
        if not hasattr(self, '_command_handler'):
            self._command_handler = self._default_command_handler

        # construct the poller
        self._poll = Poller()

        # monitoring of message stream is off by default
        self.monitor_stream = False

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        """
        The configuration_options method utilizes the arg_parser parameter to
        add arguments that should be handled during configuration.

        Keyword Arguments:
        arg_parser - argparse.ArgumentParser object.

        Sample invocation:
        >>> import argparse
        >>> parser = argparse.ArgumentParser(prog='app.py')
        >>> foo = Cornerstone()
        >>> foo.configuration_options(arg_parser=parser)
        >>> args = parser.print_usage() # doctest: +NORMALIZE_WHITESPACE
        usage: app.py [-h] [--heartbeat HEARTBEAT] [--monitor_stream]
                  [--no_block_send]
        """
        assert arg_parser

        arg_parser.add_argument('--heartbeat',
                                type=int,
                                default=3,
                                help="Set the heartbeat rate in seconds of "
                                     "the core 0mq poller timeout.")
        arg_parser.add_argument('--monitor_stream',
                                action='store_true',
                                help='Enable the sampling of message flow.')
        arg_parser.add_argument('--no_block_send',
                                action='store_true',
                                help='Enable NOBLOCK on the sending of messages.'
                                     ' This will cause an message to be dropped '
                                     'if no receiver is present.')


    def configure(self, args=None):
        """
        The configure method configures a Cornerstone instance by
        prior to the invocation of start.

        Keyword Arguments:
        args - an object with attributes set to the argument values.e
        """
        assert args


    def register_input_sock(self, sock):
        """
        Register a given input socket as the ingest point for a Cornerstone
        instance.

        Keyward Arguments:
        sock - the input socket that is to be registered.

        Return: None

        Cornerstone does not support multiple input sockets, so any currently
        registered input socket will be discarded. This is a per instance
        limitation, in which case the primary concern is ipaddress collision.

        Example Usage:
        >>> from zmq import SUB, SUBSCRIBE
        >>> foo = Cornerstone()
        >>> ctx = foo.zmq_ctx
        >>> sock1 = ctx.socket(SUB)
        >>> sock1.connect('tcp://localhost:2880')
        >>> sock1.setsockopt(SUBSCRIBE, "")
        >>> assert foo._poll.sockets == {}
        >>> foo.register_input_sock(sock1)
        >>> assert foo._poll.sockets.has_key(sock1)
        >>> sock2 = ctx.socket(SUB)
        >>> sock2.connect('tcp://localhost:2881')
        >>> sock2.setsockopt(SUBSCRIBE, "")
        >>> foo.register_input_sock(sock2)
        >>> assert not foo._poll.sockets.has_key(sock1)
        >>> assert foo._poll.sockets.has_key(sock2)
        """
        # if there is an existing input socket, then it will be removed.
        if self._input_sock is not None:
            self._poll.unregister(self._input_sock)
            self._input_sock.close()
            self._input_sock = None

        self._input_sock = sock
        if self._input_sock is not None:
            self._poll.register(self._input_sock, POLLIN)


    def register_output_sock(self, sock):
        """
        Register a given output socket as the egress point for a Cornerstone
        instance.

        Keyward Arguments:
        sock - the output socket that is to be registered.

        Return: none

        Cornerstone does not support multiple output sockets,
        so any currently registered output socket will be discarded. This is
        a per instance limitation. In which case the primary concern is
        ipaddress collision.

        Example Usage:
        >>> from zmq import PUB
        >>> foo = Cornerstone()
        >>> ctx = foo.zmq_ctx
        >>> sock1 = ctx.socket(PUB)
        >>> sock1.bind('tcp://*:2880')
        >>> assert foo._output_sock == None
        >>> foo.register_output_sock(sock1)
        >>> assert foo._output_sock == sock1
        >>> sock2 = ctx.socket(PUB)
        >>> sock2.bind('tcp://*:28881')
        >>> foo.register_output_sock(sock2)
        >>> assert foo._output_sock == sock2
        """
        # if there is an existing output socket, then it will be removed.
        if self._output_sock is not None:
            self._output_sock.close()
            self._output_sock = None

        self._output_sock = sock


    def send(self, msg):
        assert msg
        if self.monitor_stream:
            self.log.info('o: %s', msg)

        if not self.no_block_send:
            self._output_sock.send(msg)
        else:
            try:
                self._output_sock.send(msg, NOBLOCK)
            except:
                self.log.error("Unexpected error:", sys.exc_info()[0])


    def setRun(self):
        self._stop = False


    def isStopped(self):
        return self._stop


    def run(self):
        """
        Comment: -- AAA --
        What needs to occur here si to see if there is a 0mq connection
        configured. If so, then we will simply push to that connector. This
        will be the default behavior, at least for now. There should be a
        mechanism for transmitting the data out to a registered handler.
        """
        self._stop = False

        if self.log_level == INFO:
            self.log.info('Beginning run() with configuration: %s', self._args)

        #todo: raul - move this section to command configuraiton layer
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # of course this is when a command configuration layer get's added
        controller = self.zmq_ctx.socket(SUB)
        controller.connect('tcp://localhost:7885')
        controller.setsockopt(SUBSCRIBE, "")
        self._control_sock = controller
        self._poll.register(self._control_sock)
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        loop_count = 0
        input_count = 0
        while True:
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat))
                loop_count += 1
                if self.monitor_stream and (loop_count % 1000) == 0:
                    sys.stdout.write('loop(%s)' % loop_count)
                    sys.stdout.flush()

                if self._input_sock and socks.get(self._input_sock) == POLLIN:
                    #todo: raul - this whole section needs to be redone,
                    # see additional comment AAA above.
                    msg = self.input_recv_handler(self._input_sock)
                    input_count += 1
                    if self.monitor_stream: # and (input_count % 10) == 0:
                        self.log.info('i:%s- %s', input_count, msg)

                if (self._control_sock and
                    socks.get(self._control_sock) == POLLIN):
                    msg = self._control_sock.recv()
                    if self._command_handler is not None:
                        self._command_handler(msg)

                if self._stop:
                    if self.log_level == INFO:
                        self.log('Stop flag triggered ... shutting down.')
                    break

            except ZMQError, ze:
                if ze.errno == 4: # Known exception due to keyboard ctrl+c
                    if self.log_level == INFO:
                        self.log.info('System interrupt call detected.')
                else: # exit hard on unhandled exceptions
                    self.log.error('Unhandled exception in run execution:%d - %s'
                                   % (ze.errno, ze.strerror))
                    exit(-1)

        # close the sockets held by the poller
        self._control_sock.close()
        self.register_input_sock(sock=None)
        self.register_output_sock(sock=None)

        if self.log_level == INFO:
            self.log.info('Run terminated for %s', self.name)


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


    def _default_recv_handler(self, input_sock):
        """
        This is the default receiving handler for requests comming in on an
        input socket. The default handler simply takes incoming messages and
        passes them to the registed output socket.

        Return: msg -- The message that is returned from invocation of the
        recv on the input socket.
        """
        msg = input_sock.recv()
        more = input_sock.getsockopt(RCVMORE)
        if more:
            self._output_sock.send(msg, SNDMORE)
        else:
            self._output_sock.send(msg)

        return msg


    def _default_command_handler(self, msg):
        """
        This method is the default command channel message handler. It simply
        invokes a kill flag for any message received.
        """
        self.kill()
