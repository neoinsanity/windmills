#!/usr/bin/env python
from zmq import Context, PUB, RCVMORE, SNDMORE, SUB, SUBSCRIBE
from windmills.conerstone import CornerStone


__author__ = 'neoinsanity'
#
# proxy-windmill
#

class ProxyWindmill(CornerStone):
    """
    >>> from threading import Thread
    >>> import time
    >>> from zmq import Context, SUB, SUBSCRIBE
    >>> foo = ProxyWindmill()
    Proxy Windmill Initialized ...
    >>> t = Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(3)
    >>> foo.kill()
    >>> t.join(3)
    Stop flag triggered ... shutting down.
    """


    def __init__(self):
        super(ProxyWindmill, self).__init__()

        input_sock_type = SUB
        input_sock_url = 'tcp://localhost:6667'
        input_sock_filter = ''

        server_sock = self.zmq_ctx.socket(input_sock_type)
        server_sock.connect(input_sock_url)
        server_sock.setsockopt(SUBSCRIBE, input_sock_filter)
        self.register_input_sock(server_sock)

        output_sock_type = PUB
        output_sock_url = 'tcp://*:6668'

        client_sock = self.zmq_ctx.socket(output_sock_type)
        client_sock.bind(output_sock_url)
        self.register_output_sock(client_sock)

        controller = self.zmq_ctx.socket(SUB)
        controller.connect('tcp://localhost:7885')
        controller.setsockopt(SUBSCRIBE, "")
        self._control_sock = controller

        print 'Proxy Windmill Initialized ...'


if __name__ == "__main__":
    proxyWindmill = ProxyWindmill()
    proxyWindmill.run()
