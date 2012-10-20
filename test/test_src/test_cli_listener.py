import os
from threading import Thread
import time
import unittest
from windmills import CliListener
from zmq import Context, PUSH


__author__ = 'neoinsanity'


class TestCliListener(unittest.TestCase):
    def setUp(self):
        self.zmq_ctx = Context()
        self.out_sock = self.zmq_ctx.socket(PUSH)
        self.out_sock.bind('tcp://*:6678')

        d = 'test_out'
        if not os.path.exists(d):
            os.makedirs(d)


    def tearDown(self):
        self.out_sock.close()


    def test_cli_listener_default_behavior(self):
        t = self._thread_wrapped_cli_listener()
        t.start()
        self.assertTrue(t.is_alive(),
                        'The CliEmitter instance should have started.')

        self.out_sock.send('Hello')

        time.sleep(1)

        t.cli_listener.kill()

        t.join(3)
        self.assertFalse(t.is_alive(),
                         'The CliEmitter instance should have shut down.')


    def test_cli_listener_file_option(self):
        archive_file = 'test_data/archive/cli_listener_file_option._archive'
        output_file = 'test_out/cli_listener_file_option._output'
        if os.path.exists(output_file):
            os.remove(output_file)
        args = ['-f', output_file]
        t = self._thread_wrapped_cli_listener(args)
        t.start()
        self.assertTrue(t.is_alive())
        self.out_sock.send('Goodbye, Yesterday')
        time.sleep(1)
        t.cli_listener.kill()
        t.join(3)
        self.assertFalse(t.is_alive(),
                         'CliListener instance should have shutdown.')
        arch = open(archive_file, 'r').read()
        output = open(output_file, 'r').read()
        self.assertMultiLineEqual(arch, output)


    def _thread_wrapped_cli_listener(self, argv=None):
        cli_listener = CliListener(argv=argv)
        self.assertIsNotNone(cli_listener,
                             'Unable to create instance of CliListener: %s' %
                             argv)

        t = Thread(target=cli_listener.run)
        t.cli_listener = cli_listener

        return t
