from logging import DEBUG, INFO, WARNING
from os import path, remove

from windmill_test_case import WindmillTestCase, TEST_OUT

from windmills.core import Scaffold

__author__ = 'Raul Gonzalez'


class TestScaffold(WindmillTestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_default_file_logging(self):

    # The target path to the expected file created by scaffold
    log_path = path.join(TEST_OUT, 'scaffold.log')
    if path.exists(log_path):
      remove(log_path)

    # create the test subject
    argv = '--log_level info --log_path TEST_OUT'
    scaffold = Scaffold(argv=argv)

    # test to make sure that log file is generated
    self.assertTrue(path.exists(log_path))

    # test to make sure scaffold internal state is correct
    self.assertEqual(scaffold.log_path, 'TEST_OUT')
    self.assertEqual(scaffold.log_level, INFO)

  def test_app_name_file_logging(self):

    # The target path to the expected file created by scaffold
    log_path = path.join(TEST_OUT, 'Dude.log')
    if path.exists(log_path):
      remove(log_path)

    # create the test subject
    argv = '--app_name Dude --log_level debug --log_path TEST_OUT'
    scaffold = Scaffold(argv=argv)

    # test to make sure that log file is generated
    self.assertTrue(path.exists(log_path))

    # test to make sure scaffold internal state is correct
    self.assertEqual(scaffold.app_name, 'Dude')
    self.assertEqual(scaffold.log_path, 'TEST_OUT')
    self.assertEqual(scaffold.log_level, DEBUG)

  def test_explicit_log_file(self):

    # The target path to the log file
    log_path = path.join(TEST_OUT, 'the_file.log')
    if path.exists(log_path):
      remove(log_path)

    # create the test subject
    argv = '--log_level warn --log_path TEST_OUT/the_file.log'
    scaffold = Scaffold(argv=argv)

    # test to make sure that log file is generated
    self.assertTrue(path.exists(log_path))

    # test to make sure scaffold internal state is correct
    self.assertEqual(scaffold.app_name, 'Scaffold')
    self.assertEqual('./' + scaffold.log_path, log_path)
    self.assertEqual(scaffold.log_level, WARNING)
