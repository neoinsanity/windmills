from gevent import joinall, sleep, spawn
import zmq

from utils_of_test import spawn_windmill
from windmill_test_case import WindmillTestCase

from windmills.core import Shaft


__author__ = 'Raul Gonzalez'


class TestShaft(WindmillTestCase):
  def setUp(self):
    self.zmq_ctx = zmq.Context()

  def tearDown(self):
    self.zmq_ctx.destroy()

  def test_shaft_base_behavior(self):
    """A test that simply starts and stops a Shaft instance.

    This test is just to ensure that however complex other test scenarios may
    get, the most basic operation of starting and stopping Shaft is working.
    """

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

  def test_basic_remote_kill(self):
    """Test the ability to remote kill a shaft via zmq socket."""

    # setup a zmq socket to signal a remote kill to the shaft
    cmd_sock = self.zmq_ctx.socket(zmq.PUB)
    cmd_sock.bind('tcp://*:54749')

    # create the test subject
    the_spawn, shaft = spawn_windmill(Shaft)

    # test for the expected state of shaft in run mode
    self.assertIsNotNone(shaft)
    self.assertFalse(shaft.is_stopped())

    # send the kill command to the shaft instance.
    # because this is a PUB socket, multiple calls maybe required to allow
    # time for connect negotiation between PUB and SUB
    for _ in range(3):
      cmd_sock.send('kill')
      joinall([the_spawn, ], timeout=0.1)
      if the_spawn.successful():  # if spawn is done running
        break;                    # exit the message send loop

    self.assertTrue(the_spawn.successful())
    self.assertIsNone(the_spawn.exception)

    # test that the shaft is in the correct stop state
    self.assertTrue(shaft.is_stopped())

