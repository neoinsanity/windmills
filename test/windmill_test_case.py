import os
import unittest
from gevent import monkey

__author__ = 'Raul Gonzalez'

# make sure the gevent monkey patching is done
monkey.patch_all()

# Constants for managing test
TEST_OUT = './TEST_OUT/'

class WindmillTestCase(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    # make sure that the test output directory is created
    # it assumes that the current working directory is correct
    d = TEST_OUT
    if not os.path.exists(d):
      os.makedirs(d)

