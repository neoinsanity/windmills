from gevent import joinall, sleep
import zmq.green as zmq
from utils_of_test import spawn_windmill, StdOutCapture
from windmill_test_case import WindmillTestCase

from windmills.core import Crate
from windmills.utility_service import CliEmitter, CliListener

__author__ = 'Raul Gonzalez'


class TestCliListener(WindmillTestCase):
    def setUp(self):
        self.zmq_ctx = zmq.Context()

    def tearDown(self):
        self.zmq_ctx.destroy()

    def test_default_cli_listener_behavior(self):
        """Tests the default behavior of the CliListener.

        This test is validated by setting --verbose on the CliListener instance,
        and then capturing the log output to stdout.
        """
        with StdOutCapture() as output:
            push_sock = self.zmq_ctx.socket(zmq.PUSH)
            push_sock.bind('tcp://*:60053')

            try:
                the_spawn, cli_listener = spawn_windmill(CliListener)
                self.assertFalse(cli_listener.is_stopped())

                # test message
                crate = Crate(msg_data='hola')
                push_sock.send(crate.dump)

                # wait on the message delivery
                joinall([the_spawn, ], timeout=0.1)

                # test shutdown
                cli_listener.kill()
                sleep(0)  # yield to allow shutdown

                self.assertTrue(cli_listener.is_stopped())

            finally:
                push_sock.close()

        self.assertEqual(
            output,
            ['{"call_ctx": {}, "msg_ctx": {}, "msg_data": "hola"}'],
            ('Unexpected output to stdout: %s' % output))


    def test_default_cli_emitter_behavior(self):
        pull_sock = self.zmq_ctx.socket(zmq.PULL)
        pull_sock.bind('tcp://*:60053')

        try:
            sleep(0)

            the_spawn, cli_emitter = spawn_windmill(CliEmitter)

            msg = pull_sock.recv_multipart()

            self.assertIsNotNone(msg)

            self.assertFalse(cli_emitter.is_stopped())

            joinall([the_spawn], timeout=0.1)

            self.assertTrue(cli_emitter.is_stopped)
        finally:
            pull_sock.close()
