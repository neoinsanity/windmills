import signal
from zmq import Context, Poller, POLLIN, RCVMORE, SNDMORE
from zmq.core.error import ZMQError


__author__ = 'neoinsanity'


class CornerStone(object):
    """
    >>> import threading
    >>> import time
    >>> from zmq import Context, SUB, SUBSCRIBE
    >>> foo = CornerStone()
    >>> t = threading.Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(3)
    >>> foo.kill()
    >>> t.join(1)
    Stop flag triggered ... shutting down.
    >>> # socket to receive control messages on
    >>> context = Context()
    >>> foo._control_sock = context.socket(SUB)
    >>> foo._control_sock.connect('tcp://localhost:6670')
    >>> foo._control_sock.setsockopt(SUBSCRIBE, "")
    >>> t = threading.Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(3)
    >>> foo.kill()
    >>> t.join(3)
    Stop flag triggered ... shutting down.
    """


    def __init__(self):
        self._input_sock = None
        self._output_sock = None
        self._control_sock = None

        # configure the interrupt handling
        self.stop = False
        signal.signal(signal.SIGINT, self._signal_interrupt_handler)

        # a regular hearbeat interval should be maintained.
        self.heartbeat_seconds = 3 # seconds

        # create the zmq context
        self.zmq_ctx = Context()

        # construct the poller
        self._poll = Poller()


    def register_input_sock(self, sock):
        """
        This method will register the input socket. It will only allow for a single input socket to be registered
        with any given instance. If an existing socket is registered, it will be replaced with the given sock
        parameter.

        >>> from zmq import SUB, SUBSCRIBE
        >>> foo = CornerStone()
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
        self._poll.register(sock)


    def register_output_sock(self, sock):
        """
        This method will register the output socket. It will only allow for a single output socket to be registered
        for any given instance. If an existing socket is registered, it will be replaced,
        with the given sock parameter.

        >>> from zmq import PUB
        >>> foo = CornerStone()
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
        '''
        Comment: -- AAA --
        What needs to occur here si to see if there is a 0mq connection configured. If so,
        then we will simply push to that connector. This will be the default behavior, at least for now.
        There should be a mechanism for transmitting the data out to a registered handler.
        '''
        self._stop = False

        if self._input_sock:
            self._poll.register(self._input_sock, POLLIN)

        if self._control_sock:
            self._poll.register(self._control_sock, POLLIN)

        while True:
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat_seconds))
            except ZMQError, ze:
                if ze.errno == 4:
                    print 'System interrupt call detected.'
                else: # exit hard on unhandled exceptions
                    print 'Unhandled exception in run execution:', ze.errno, '-', ze.strerror
                    exit(-1)

            if self._input_sock and socks.get(self._input_sock) == POLLIN:
                #todo: raul - this whold section needs to be redone, see additional comment AAA above.
                msg = self._input_sock.recv()
                more = self._input_sock.getsockopt(RCVMORE)
                if more:
                    self._output_sock.send(msg, SNDMORE)
                else:
                    self._output_sock.send(msg)

            if self._control_sock and socks.get(self._control_sock) == POLLIN:
                self._control_sock.recv()
                print 'Got kill command'
                break

            if self._stop:
                print 'Stop flag triggered ... shutting down.'
                break


    def kill(self):
        """
        This method will shut down the running loop if run() method has been invoked.
        """
        self._stop = True


    def _signal_interrupt_handler(self, signum, frame):
        """
        This method is registered with the signal library to ensure handling of system interrupts. Initialization of
        this method is performed during __init__ invocation.
        """
        self.kill()


    def _default_command_handler(self, msg):
        """
        This method is the default command channel message handler. It simple invokes a kill flag.
        """
        self.kill()
