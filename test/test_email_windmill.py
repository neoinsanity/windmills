import os
import time
from mock import  MagicMock, patch
from test.windmill_test_case import WindmillTestCase
from test.utils_of_test import ( thread_wrap_windmill)
from zmq import Context, PUB, PUSH


__author__ = 'neoinsanity'


class TestEmailWindmill(WindmillTestCase):
    def setUp(self):
        self.zmq_ctx = Context()

        push_out_sock = self.zmq_ctx.socket(PUSH)
        push_out_sock.bind('tcp://*:6678')
        pub_out_sock = self.zmq_ctx.socket(PUB)
        pub_out_sock.connect('tcp://localhost:6679')

        self.sock_map = {
            'PUSH': push_out_sock,
            'PUB': pub_out_sock
        }

        d = 'test_out'
        if not os.path.exists(d):
            os.makedirs(d)


    def tearDown(self):
        for sock in list(self.sock_map.values()):
            sock.close()


    @patch('socket.SMTP', autospec=True)
    def _test_email_default_behavior(self, smtp_mock):
    #with patch('sock.SMTP', autospec=True) as mock_smtp:
        #define mock behavior
        mock_smtp_object = MagicMock()
        smtp_mock.side_effect = mock_smtp_object

        t = thread_wrap_windmill('EmailWindmill', argv=[])
        assert t

        try:
            t.start()
            self.assertTrue(t.is_alive(),
                            'The EmailWindmill instance should have started.')
            self.sock_map['PUSH'].send(
                '{"type":"email_request","payload" : {"msg" : "Hi, this is a message that has been delivered through email service as a test.\nNeeded '
                'multi '
                'recipient test.\n\n share and enjoy", "subject" : "A message from email send service.", "sender" : "raul@filepicker.io",'
                '"to" : ["raul@filepicker.io"]}}')
            time.sleep(1)
        finally:
            t.windmill.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'The EmailWindmill instance should have shut down.')

        #    @patch('socket', autospec=True)


    def _test_email_sub_behavior(self):
    #with patch('sock.SMTP', autospec=True) as mock_smtp:
        #define mock behavior
        mock_smtp_object = MagicMock()
        #smtp_mock.SMTP.side_effect = mock_smtp_object

        args = '--input_sock_url tcp://*:6679 --input_bind --input_sock_type SUB --verbose --monitor_stream'
        t = thread_wrap_windmill('EmailWindmill', argv=args.split())
        assert t

        try:
            t.start()
            self.assertTrue(t.is_alive(),
                            'The EmailWindmill instance should have started.')
            self.sock_map['PUB'].send(
                '{"type":"email_request","payload" : {"msg" : "Hi, this is a message that has been delivered through email service as a test. \\nNeeded multi recipient test. share and enjoy", "subject" : "A message from email send service.", "sender" : "raul@filepicker.io","to" : ["raul@filepicker.io"]}}')
            time.sleep(1)
        finally:
            t.windmill.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'The EmailWindmill instance should have shut down.')

