from os import path, remove
from gevent import joinall, sleep
import zmq.green as zmq

from utils_of_test import StdOutCapture, spawn_windmill
from windmill_test_case import WindmillTestCase, TEST_OUT

from windmills.core.crate import Crate
from windmills.utility_service import CliListener

__author__ = 'Raul Gonzalez'


class TestCliListener(WindmillTestCase):
  def setUp(self):
    self.zmq_ctx = zmq.Context()
    push_out_sock = self.zmq_ctx.socket(zmq.PUSH)
    push_out_sock.bind('tcp://*:60053')
    pub_out_sock = self.zmq_ctx.socket(zmq.PUB)
    pub_out_sock.bind('tcp://*:8332')

    self.sock_map = {
      'PUSH': push_out_sock,
      'PUB': pub_out_sock
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
      the_spawn, cli_listener = spawn_windmill(CliListener)

      self.assertFalse(cli_listener.is_stopped())

      # test message
      crate = Crate(msg_data='hola')
      self.sock_map['PUSH'].send(crate.dump)

      # wait on the message delivery
      joinall([the_spawn, ], timeout=0.1)

      # test shutdown
      cli_listener.kill()
      sleep(0)  # yield to allow shutdown

      self.assertTrue(cli_listener.is_stopped())

    # END OF WITH
    self.assertEqual(
      output,
      ['{"call_ctx": {}, "msg_ctx": {}, "msg_data": "hola"}'],
      ('Unexpected output to stdout: %s' % output))

  def test_file_output(self):

    # ensure the file does not exist, to prevent false positives
    file_path = path.join(TEST_OUT, 'test_cli_listener_file_output.out')
    if path.exists(file_path):
      remove(file_path)

    # create the test subject
    argv = '--f ' + file_path
    the_spawn, cli_listener = spawn_windmill(CliListener, argv=argv)

    # test message
    crate = Crate(msg_data='Hola mundo')
    self.sock_map['PUSH'].send(crate.dump)

    sleep(0)
    cli_listener.kill()

    # wait on the message delivery
    joinall([the_spawn, ], timeout=1)
    self.assertIsNone(the_spawn.exception)
    self.assertTrue(cli_listener.is_stopped())

    # ensure the message logged to file
    self.assertTrue(path.exists(file_path),
                    'The file should exist: %s' % file_path)

