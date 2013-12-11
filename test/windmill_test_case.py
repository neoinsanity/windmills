import os
import unittest
import zmq.green as zmq

__author__ = 'Raul Gonzalez'

# Standard directory for test file
TEST_OUT = './TEST_OUT/'


class WindmillTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # make sure that the test output directory is created
        # it assumes that the current working directory is correct
        d = TEST_OUT
        if not os.path.exists(d):
            os.makedirs(d)

    @classmethod
    def get_bind_socket(cls, sock_type=zmq.PUSH, bind=True):
        port_selected = None
