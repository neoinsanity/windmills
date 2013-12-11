from  gevent import spawn
import json
from crate import Crate

__author__ = 'Raul Gonzalez'


class Blade(object):
    def __init__(self, handler=None, shaft=None):
        # call handler
        self.handler = handler
        self.shaft = shaft

    def recv_handler(self, sock):
        assert sock
        msg_json = sock.recv()
        msg = json.loads(msg_json)
        crate = Crate(msg['call_ctx'], msg['msg_ctx'], msg['msg_data'])

        # allow handling in another thread
        spawn(self.handler, crate)
