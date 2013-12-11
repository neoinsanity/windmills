from  gevent import spawn
import json
from crate import Crate

__author__ = 'Raul Gonzalez'


class Blade(object):
    def __init__(self, handler=None, socket_config=None):
        """

        :param handler:
        :type handler: MethodType or FunctionType
        :param socket_config:
        :type socket_config: super_core.OutputSocketConfig
        """
        self._handler = handler
        self._socket_config = socket_config

    def recv_handler(self, sock):
        assert sock
        msg_json = sock.recv()
        msg = json.loads(msg_json)
        crate = Crate(msg['call_ctx'], msg['msg_ctx'], msg['msg_data'])

        # allow handling in another thread
        spawn(self._handler, crate)
