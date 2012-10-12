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
from miller import Miller
import signal
import sys
from zmq import (Context, Poller, POLLIN, RCVMORE, SNDMORE, SUB, SUBSCRIBE,
                 ZMQError)


__author__ = 'neoinsanity'


class Cornerstone(Miller):
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
    >>> time.sleep(3)
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
    >>> time.sleep(3)
    >>> foo.kill()
    >>> t.join(1)
    >>> assert not t.is_alive()
    """


    def __init__(self, **kwargs):
        self._input_sock = None
        self._output_sock = None
        self._control_sock = None

        # configure the interrupt handling
        self.stop = False
        signal.signal(signal.SIGINT, self._signal_interrupt_handler)

        # a regular hearbeat interval must be set to the default.
        self.heartbeat = 3 # seconds

        # create the zmq context
        self.zmq_ctx = Context()

        # create the default handler, if none has been assigned.
        if not hasattr(self, '_control_handler'):
            self._control_handler = self._default_command_handler

        # construct the poller
        self._poll = Poller()

        # verbose level is off by default
        self.verbose = False

        # monitoring of message stream is off by default
        self.monitor_stream = False


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
        usage: app.py [-h] [--heartbeat HEARTBEAT] [--monitor_stream]\
        [--verbose]
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
        arg_parser.add_argument('--verbose',
                                action="store_true",
                                help='Enable verbose log output. Useful for '
                                     'debugging.')


    def configure(self, args=None):
        """
        The configure method configures a Cornerstone instance by
        prior to the invocation of start.

        Keyword Arguments:
        args - an object with wttributes set to the argument values.

        Example Usage:
        >>> foo = Cornerstone()
        >>> args = foo.__create_property_bag__()
        >>> args.heartbeat = 5
        >>> args.monitor_stream = True
        >>> args.verbose = True
        >>> foo.configure(args=args)
        >>> assert foo.heartbeat == 5
        >>> assert foo.monitor_stream == True
        >>> assert foo.verbose == True
        """
        assert args
        if hasattr(args, 'heartbeat'):
            self.heartbeat = args.heartbeat
        if hasattr(args, 'monitor_stream'):
            self.monitor_stream = args.monitor_stream
        if hasattr(args, 'verbose'):
            self.verbose = args.verbose

        #todo: raul - move this section to command configuraiton layer
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # of course this is when a command configuration layer get's added
        controller = self.zmq_ctx.socket(SUB)
        controller.connect('tcp://localhost:7885')
        controller.setsockopt(SUBSCRIBE, "")
        self._control_sock = controller
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
            self._input_sock = None

        self._input_sock = sock
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
            self._output_sock = None

        self._output_sock = sock


    def run(self):
        """
        Comment: -- AAA --
        What needs to occur here si to see if there is a 0mq connection
        configured. If so, then we will simply push to that connector. This
        will be the default behavior, at least for now. There should be a
        mechanism for transmitting the data out to a registered handler.
        """
        self._stop = False

        if self.verbose:
            print 'Beginning run() with state:', str(self)

        loop_count = 0
        input_count = 0
        while True:
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat))
                loop_count += 1
                if self.monitor_stream and (loop_count % 100) == 0:
                    sys.stdout.write('loop(%s)' % loop_count)
                    sys.stdout.flush()
            except ZMQError, ze:
                if ze.errno == 4: # Known exception due to keyboard ctrl+c
                    if self.verbose:
                        print 'System interrupt call detected.'
                else: # exit hard on unhandled exceptions
                    print ('Unhandled exception in run execution:%d - %s'
                           % (ze.errno, ze.strerror))
                    exit(-1)

            if self._input_sock and socks.get(self._input_sock) == POLLIN:
                #todo: raul - this whole section needs to be redone,
                # see additional comment AAA above.
                msg = self._input_sock.recv()
                more = self._input_sock.getsockopt(RCVMORE)
                if more:
                    self._output_sock.send(msg, SNDMORE)
                else:
                    self._output_sock.send(msg)
                input_count += 1
                if self.monitor_stream and (input_count % 10) == 0:
                    print '.', input_count, '-', msg

            if self._control_sock and socks.get(self._control_sock) == POLLIN:
                msg = self._control_sock.recv()
                if self._control_handler is not None:
                    self._control_handler(msg)

            if self._stop:
                if self.verbose:
                    print 'Stop flag triggered ... shutting down.'
                break


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


    def _default_command_handler(self, msg):
        """
        This method is the default command channel message handler. It simply
        invokes a kill flag for any message received.
        """
        self.kill()
