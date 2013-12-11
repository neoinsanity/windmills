from schematics.models import Model
from schematics.types import StringType, BooleanType, IntType
import zmq


__author__ = 'Raul Gonzalez'


#: Mapping for zmq_socket_types
ZMQ_INPUT_SOCKET_TYPE = {
    'pull': zmq.PULL,
    'rep': zmq.REP,
    'sub': zmq.SUB,
    'router': zmq.ROUTER,
}

ZMQ_OUTPUT_SOCKET_TYPE = {
    'pub': zmq.PUB,
    'push': zmq.PUSH,
    'req': zmq.REQ,
    'dealer': zmq.REQ,
}

ZMQ_SOCKET_TYPES = dict()
ZMQ_SOCKET_TYPES.update(ZMQ_INPUT_SOCKET_TYPE.items())
ZMQ_SOCKET_TYPES.update(ZMQ_OUTPUT_SOCKET_TYPE.items())

DEFAULT_INPUT_OPTIONS = {
    'url': 'tcp://localhost:60053',
    'sock_type': 'pull',
    'sock_filter': '',
    'sock_bind': False,
    'linger': 0,
    'monitor_stream': False,
    'no_block_send': False,
}

DEFAULT_OUTPUT_OPTIONS = {
    'url': 'tcp://localhost:60053',
    'sock_type': 'push',
    'sock_bind': False,
    'linger': 0,
    'monitor_stream': False,
    'no_block_send': False,
}


class SocketConfig(Model):
    url = StringType(required=True)
    sock_type = StringType(choices=ZMQ_SOCKET_TYPES.keys(), required=True)
    sock_filter = StringType(default='')
    sock_bind = BooleanType(default=False, required=False)
    linger = IntType(default=0, required=False)
    monitor_stream = BooleanType(default=False, required=False)
    no_block_send = BooleanType(default=False, required=False)

    @property
    def zmq_sock_type(self):
        return ZMQ_SOCKET_TYPES[self.sock_type]


class InputSocketConfig(SocketConfig):
    sock_type = StringType(choices=ZMQ_INPUT_SOCKET_TYPE.keys(), required=True)


class OutputSocketConfig(SocketConfig):
    sock_type = StringType(choices=ZMQ_OUTPUT_SOCKET_TYPE.keys(), required=True)
