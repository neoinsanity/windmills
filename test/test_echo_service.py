import os
from test.utils_of_test import thread_wrap_windmill
from test.windmill_test_case import WindmillTestCase
from zmq import Context


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
        t = thread_wrap_windmill('EchoService')

