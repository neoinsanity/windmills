import os
from test.utils_of_test import thread_wrap_windmill
from test.windmill_test_case import WindmillTestCase
from zmq import Context, REQ


__author__ = 'neoinsanity'


class TestEchoService(WindmillTestCase):
    def setUp(self):
        self.zmq_ctx = Context()

        d = 'test_out'
        if not os.path.exists(d):
            os.makedirs(d)


    def tearDown(self):
        pass


    def test_echo_service_default_behavior(self):
        req_out_sock = self.zmq_ctx.socket(REQ)
        req_out_sock.bind('tcp://*:8889')

        t = thread_wrap_windmill('EchoService')

        try:
            t.start()
            self.assertTrue(t.is_alive,
                            'The EchoService instance should have started.')
            req_out_sock.send("echo, echo, echo")
            msg = req_out_sock.recv()

            self.assertEqual("echo, echo, echo", msg)
        finally:
            t.windmill.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'The EchoService instance should have shutdown.')

            req_out_sock.close()


    def test_echo_service_options(self):
        req_out_sock = self.zmq_ctx.socket(REQ)
        req_out_sock.bind('tcp://*:8899')

        argv = ['-m', 'pong', '--reply_sock_url', 'tcp://localhost:8899']
        t = thread_wrap_windmill('EchoService', argv=argv)
        try:
            t.start()
            self.assertTrue(t.is_alive(),
                            'The EchoService instance should have started.')
            req_out_sock.send('ping')
            msg = req_out_sock.recv()

            self.assertEqual('pong', msg)
        finally:
            t.windmill.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'The EchoService instance shold have shutdown.')

            req_out_sock.close()
