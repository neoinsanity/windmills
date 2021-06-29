from gevent import joinall, sleep
import zmq.green as zmq

from .utils_of_test import spawn_windmill
from .windmill_test_case import WindmillTestCase

from windmills.utility_service.cli_emitter import CliEmitter

__author__ = 'Raul Gonzalez'


class TestCliEmitter(WindmillTestCase):
    def setUp(self):
        self.zmq_ctx = zmq.Context()

    def tearDown(self):
        self.zmq_ctx.destroy()

