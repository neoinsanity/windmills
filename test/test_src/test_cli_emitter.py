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
        args = ['-f', output_file,
                '--input_sock_url', 'tcp://localhost:6677']
        t = thread_wrapped_cli_listener(args)

        try:
            t.start()
            self.assertTrue(t.is_alive())
            time.sleep(1)
            emitter.run()
        finally:
            t.cli_listener.kill()
            t.join(3)
            self.assertFalse(t.is_alive(),
                             'CliListener instance should have shutdown.')

        self.assertFiles(archive_file, output_file)

