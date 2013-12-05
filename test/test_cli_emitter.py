import os
from windmills.utility_service.cli_emitter import CliEmitter
from utils_of_test import gen_archive_output_pair

__author__ = 'Raul Gonzalez'


class TestCliEmitter():
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_cli_emitter_default_behavior(self):
    archive_file, output_file = gen_archive_output_pair(
      'cli_emitter_default_behavior')

    emitter = CliEmitter()
    assert emitter
