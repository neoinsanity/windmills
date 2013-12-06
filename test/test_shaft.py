from gevent import joinall, sleep, spawn
import zmq.green as zmq

from utils_of_test import spawn_windmill
from windmill_test_case import WindmillTestCase

from windmills.core import Shaft

__author__ = 'Raul Gonzalez'


class TestShaft(WindmillTestCase):
  def setUp(self):
    self.zmq_ctx = zmq.Context()

  def tearDown(self):
    self.zmq_ctx.destroy()

  def test_shaft_default_behavior(self):

    shaft = Shaft()

    # before starting, the shaft should be in a stopped state
    self.assertTrue(shaft.is_stopped())

    the_spawn = spawn(shaft.run)
    sleep(0)  # give the spawn a chance to begin run

    self.assertTrue(the_spawn.started)
    self.assertFalse(shaft.is_stopped())

    shaft.kill()

    joinall([the_spawn], timeout=1)

    # test to make sure that the shaft has successfully stopped
    self.assertTrue(the_spawn.successful())
    self.assertIsNone(the_spawn.exception)

    # test that the shaft is in the correct stop state
    self.assertTrue(shaft.is_stopped())

  def test_shaft_remote_kill(self):

    # setup a zmq socket to signal a remote kill to the shaft
    cmd_sock = self.zmq_ctx.socket(zmq.PAIR)
    cmd_sock.bind('tcp://*:54749')

    # create the test subject
    the_spawn, shaft = spawn_windmill(Shaft)

    # test for the expected state of shaft in run mode
    self.assertIsNotNone(shaft)
    self.assertFalse(shaft.is_stopped())

    # send the kill command
    cmd_sock.send('kill')

    # verify and validate shaft shutdown
    joinall([the_spawn], timeout=1)
    self.assertIsNone(the_spawn.exception)

    # test that the shaft is in the correct stop state
    self.assertTrue(shaft.is_stopped())

