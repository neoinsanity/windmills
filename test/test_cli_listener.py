from gevent import joinall, sleep
import zmq.green as zmq

from utils_of_test import StdOutCapture, spawn_windmill
from windmill_test_case import WindmillTestCase

from windmills.core.crate import Crate
from windmills.utility_service import CliListener

__author__ = 'Raul Gonzalez'


class TestCliListener(WindmillTestCase):
  def setUp(self):
    self.zmq_ctx = zmq.Context()
    pair_out_sock = self.zmq_ctx.socket(zmq.PAIR)
    pair_out_sock.bind('tcp://*:60053')
    push_out_sock = self.zmq_ctx.socket(zmq.PUSH)
    push_out_sock.bind('tcp://*:6678')
    pub_out_sock = self.zmq_ctx.socket(zmq.PUB)
    pub_out_sock.bind('tcp://*:6679')

    self.sock_map = {
      'PAIR': pair_out_sock,
      'PUSH': push_out_sock,
      'PUB': push_out_sock
    }

  def tearDown(self):
    for sock in self.sock_map.values():
      sock.close()

    self.zmq_ctx.destroy()

  def test_default_behavior(self):
    """Tests the default behavior of the CliListener.

    This test is validated by setting --verbose on the CliListener instance,
    and then capturing the log output to stdout.
    """
    with StdOutCapture() as output:
      argv = '--verbose'
      the_spawn, cli_listener = spawn_windmill(CliListener, argv)

      self.assertFalse(cli_listener.is_stopped())

      # test message
      crate = Crate(msg_data='hello')
      self.sock_map['PAIR'].send(crate.dump)

      # wait on the message delivery
      joinall([the_spawn, ], timeout=0.1)

      # test shutdown
      cli_listener.kill()
      sleep(0)  # yield to allow shutdown

      self.assertTrue(cli_listener.is_stopped())

    self.assertEqual(
      output,
      ['{"call_ctx": {}, "msg_ctx": {}, "msg_data": "hello"}', 'hello'])
