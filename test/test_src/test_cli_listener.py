import os
from threading import Thread
import time
import unittest
from windmills import CliListener
from zmq import Context, PUB, PUSH


__author__ = 'neoinsanity'


class TestCliListener(unittest.TestCase):
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
        t = self._thread_wrapped_cli_listener()
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
        archive_file, output_file = self._gen_archive_output_pair(
            'cli_listener_file_option')

        args = ['-f', output_file]
        self._deliver_the_message('Goodbye, Yesterday', args)

        arch = open(archive_file, 'r').read()
        output = open(output_file, 'r').read()
        self.assertMultiLineEqual(arch, output)


    def test_cli_socket_type_option(self):
        archive_file, output_file = self._gen_archive_output_pair(
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

        arch = open(archive_file, 'r').read()
        output = open(output_file, 'r').read()
        self.assertMultiLineEqual(arch, output)


    def _deliver_the_messages(self, msgs=[], args=list(), sock_type='PUSH'):
        t = self._thread_wrapped_cli_listener(args)
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
        t = self._thread_wrapped_cli_listener(args)
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


    def _gen_archive_output_pair(self, test_name=None ):
        archive_file = 'test_data/archive/' + test_name + '._archive'
        output_file = 'test_out/' + test_name + '._output'

        if os.path.exists(output_file):
            os.remove(output_file)

        return archive_file, output_file


    def _thread_wrapped_cli_listener(self, argv=None):
        cli_listener = CliListener(argv=argv)
        self.assertIsNotNone(cli_listener,
                             'Unable to create instance of CliListener: %s' %
                             argv)

        t = Thread(target=cli_listener.run)
        t.cli_listener = cli_listener

        return t
