import signal
import sys
from zmq import Context, Poller, POLLIN, RCVMORE, SNDMORE
from zmq.core.error import ZMQError
from miller import Miller


__author__ = 'neoinsanity'


class Cornerstone(Miller):
    """
    >>> import threading
    >>> import time
    >>> from zmq import Context, SUB, SUBSCRIBE
    >>> foo = Cornerstone()
    >>> t = threading.Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(3)
    >>> foo.kill()
    >>> t.join(6)
    Stop flag triggered ... shutting down.
    >>> # socket to receive control messages on
    >>> ctx = foo.zmq_ctx
    >>> sock = ctx.socket(SUB)
    >>> sock.connect('tcp://localhost:6670')
    >>> sock.setsockopt(SUBSCRIBE, "")
    >>> foo.register_input_sock(sock)
    >>> t = threading.Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(3)
    >>> foo.kill()
    >>> t.join(3)
    Stop flag triggered ... shutting down.
    """


    def __init__(self, *args, **kwargs):
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


    def configuration_options(self, arg_parser=None):
        assert arg_parser
        arg_parser.add_argument('--heartbeat',
                                type=int,
                                default=3,
                                help="Set the heartbeat rete in seconds of "
                                     "the core 0mq poller.")


    def configure(self, args=None):
        self.heartbeat = args.heartbeat;


    def register_input_sock(self, sock):
        """
        This method will register the input socket. It will only allow for a
        single input socket to be registered with any given instance. If an
        existing socket is registered, it will be replaced with the given sock
        parameter.

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
        This method will register the output socket. It will only allow for a
        single output socket to be registered for any given instance. If an
        existing socket is registered, it will be replaced with the given
        socket for output handling.

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
        self._poll.register(self._control_sock, POLLIN)


    def run(self):
        '''
        Comment: -- AAA --
        What needs to occur here si to see if there is a 0mq connection
        configured. If so,
        then we will simply push to that connector. This will be the default
        behavior, at least for now.
        There should be a mechanism for transmitting the data out to a
        registered handler.
        '''
        self._stop = False

        tick = 0
        while True:
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat))
            except ZMQError, ze:
                if ze.errno == 4:
                    print 'System interrupt call detected.'
                else: # exit hard on unhandled exceptions
                    print 'Unhandled exception in run execution:', ze.errno,\
                    '-', ze.strerror
                    exit(-1)

            if self._input_sock and socks.get(self._input_sock) == POLLIN:
                #todo: raul - this whold section needs to be redone,
                # see additional comment AAA above.
                msg = self._input_sock.recv()
                more = self._input_sock.getsockopt(RCVMORE)
                if more:
                    self._output_sock.send(msg, SNDMORE)
                else:
                    self._output_sock.send(msg)
                tick += 1
                if(tick % 100) == 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()

            if self._control_sock and socks.get(self._control_sock) == POLLIN:
                msg = self._control_sock.recv()
                if self._control_handler is not None:
                    self._control_handler(msg)

            if self._stop:
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
