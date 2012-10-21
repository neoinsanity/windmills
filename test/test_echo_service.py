import os
from test.utils_of_test import thread_wrap_windmill
from test.windmill_test_case import WindmillTestCase
from zmq import Context, REQ


__author__ = 'neoinsanity'


class TestEchoService(WindmillTestCase):
    def setUp(self):
        self.zmq_ctx = Context()
        self.req_out_sock = self.zmq_ctx.socket(REQ)
        self.req_out_sock.bind('tcp://*:8889')

        d = 'test_out'
        if not os.path.exists(d):
            os.makedirs(d)


    def tearDown(self):
        self.req_out_sock.close()


    def test_echo_service_default_behavior(self):
        t = thread_wrap_windmill('EchoService')
        try:
            t.start()
            self.assertTrue(t.is_alive,
                            'The EchoService instance shouldj have started.')
            self.req_out_sock.send("echo, echo, echo")
            msg = self.req_out_sock.recv()

            self.assertEqual("echo, echo, echo", msg)
        finally:
            t.windmill.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'The EchoService instance should have shutdown.')
