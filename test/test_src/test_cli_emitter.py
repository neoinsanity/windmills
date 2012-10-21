import os
import time
from windmill_test_case import WindmillTestCase
from utils_of_test import (gen_archive_output_pair, thread_wrapped_cli_listener)
from windmills import CliEmitter


__author__ = 'neoinsanity'


class TestCliEmitter(WindmillTestCase):
    def setUp(self):
        d = 'test_out'
        if not os.path.exists(d):
            os.makedirs(d)


    def tearDown(self):
        pass


    def test_cli_emitter_default_hehaviour(self):
        archive_file, output_file = gen_archive_output_pair(
            'cli_emitter_default_behavior')

        emitter = CliEmitter()
        assert emitter

        # create the listener and direct it's output to out_file
        t = thread_wrapped_cli_listener(argv=[
            '-f', output_file,
            '--input_sock_url', 'tcp://localhost:6677'])
        assert t

        self.emit_message(emitter, t)

        self.assertFiles(archive_file, output_file)


    def test_cli_emitter_message_option(self):
        self.executor(
            test_name='cli_emitter_message_option',
            emitter_args=[
                '-m', 'different message'],
            listener_args=[
                '--input_sock_url', 'tcp://localhost:6677'])


    def test_cli_emitter_file_option(self):
        self.executor(
            test_name='cli_emitter_file_option',
            emitter_args=[
                '-f', 'test_data/inputs/cli_emitter_file_option._input'],
            listener_args=[
                '--input_sock_url', 'tcp://localhost:6677'])


    def executor(self,
                 test_name=None,
                 emitter_args=None,
                 listener_args=None):
        assert test_name
        archive_file, output_file = gen_archive_output_pair(test_name)

        emitter = CliEmitter(argv=emitter_args)
        assert emitter

        # add the output file to the listener arguments
        listener_args = ['-f', output_file] + listener_args
        # create the listener and direct it's output to out_file
        t = thread_wrapped_cli_listener(argv=listener_args)
        assert t

        self.emit_message(emitter, t)

        self.assertFiles(archive_file, output_file)


    def emit_message(self, emitter=None, listener_thread=None):
        try:
            listener_thread.start()
            self.assertTrue(listener_thread.is_alive())
            time.sleep(1)
            emitter.run()
        finally:
            listener_thread.cli_listener.kill()
            listener_thread.join(3)
            self.assertFalse(listener_thread.is_alive(),
                             'CliListener instance should have shutdown.')
