import os
import time
from utils_of_test import (gen_archive_output_pair,
                           thread_wrapped_cli_listener)
from windmill_test_case import WindmillTestCase
from zmq import Context, PUB, PUSH


__author__ = 'neoinsanity'


class TestCliListener(WindmillTestCase):
    def setUp(self):
        self.zmq_ctx = Context()
        push_out_sock = self.zmq_ctx.socket(PUSH)
        push_out_sock.bind('tcp://*:6678')
        pub_out_sock = self.zmq_ctx.socket(PUB)
        pub_out_sock.bind('tcp://*:6679')

        self.sock_map = {
            'PUSH': push_out_sock,
            'PUB': pub_out_sock
        }

        d = 'test_out'
        if not os.path.exists(d):
            os.makedirs(d)


    def tearDown(self):
        for sock in self.sock_map.values():
            sock.close()


    def test_cli_listener_default_behavior(self):
        t = thread_wrapped_cli_listener()
        try:
            t.start()
            self.assertTrue(t.is_alive(),
                            'The CliEmitter instance should have started.')
            self.sock_map['PUSH'].send('Hello')
            time.sleep(1)
        finally:
            t.cli_listener.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'The CliEmitter instance should have shut down.')


    def test_cli_listener_file_option(self):
        archive_file, output_file = gen_archive_output_pair(
            'cli_listener_file_option')

        args = ['-f', output_file]
        self._deliver_the_message('Goodbye, Yesterday', args)

        self.assertFiles(archive_file, output_file)


    def test_cli_socket_type_option(self):
        archive_file, output_file = gen_archive_output_pair(
            'cli_socket_type_option')

        args = ['-f', output_file,
                '--input_sock_type', 'SUB',
                '--input_sock_filter', 'cat',
                '--input_sock_url', 'tcp://localhost:6679']

        self._deliver_the_messages(['throw away\n',
                                    'dog house\n',
                                    'cat people\n',
                                    'dog nap\n',
                                    'cat scratch\n'],
                                   args, 'PUB')

        self.assertFiles(archive_file, output_file)


    def _deliver_the_messages(self, msgs=[], args=list(), sock_type='PUSH'):
        t = thread_wrapped_cli_listener(args)
        try:
            t.start()
            self.assertTrue(t.is_alive())
            for msg in msgs:
                self.sock_map[sock_type].send(msg)
                time.sleep(0.5)
            time.sleep(1)
        finally:
            t.cli_listener.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'CliListener instance should have shutdown.')


    def _deliver_the_message(self, msg=None, args=list(), sock_type='PUSH'):
        t = thread_wrapped_cli_listener(args)
        try:
            t.start()
            self.assertTrue(t.is_alive())
            self.sock_map[sock_type].send(msg)
            time.sleep(1)
        finally:
            t.cli_listener.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'CliListener instance should have shutdown.')

