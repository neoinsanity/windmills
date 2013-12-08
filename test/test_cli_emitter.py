from gevent import joinall, sleep
import zmq.green as zmq

from utils_of_test import spawn_windmill
from windmill_test_case import WindmillTestCase

from windmills.utility_service.cli_emitter import CliEmitter

__author__ = 'Raul Gonzalez'


class TestCliEmitter(WindmillTestCase):
  def setUp(self):
    self.zmq_ctx = zmq.Context()

  def tearDown(self):
    self.zmq_ctx.destroy()


  def test_default_behavior(self):

    push_sock = self.zmq_ctx.socket(zmq.PUSH)
    push_sock.bind('tcp://*:60053')
    the_spawn, cli_emitter = spawn_windmill(CliEmitter)

    self.assertFalse(cli_emitter.is_stopped())

    cli_emitter.kill()

    joinall([the_spawn], timeout=0.1)

    self.assertTrue(cli_emitter.is_stopped)
