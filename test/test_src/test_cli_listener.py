import unittest
from windmills import CliListener


__author__ = 'neoinsanity'


class TestCliListener(unittest.TestCase):
    def test_default_cli_listener_behavior(self):
        cli_listener = CliListener()
        self.assertIsNotNone(cli_listener,
                             'Unable to create default instance of CliListener')
