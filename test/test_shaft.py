from gevent import joinall, sleep, spawn
import zmq.green as zmq

from windmill_test_case import WindmillTestCase

from windmills.core import Shaft

__author__ = 'Raul Gonzalez'


class TestShaft(WindmillTestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_shaft_default_behavior(self):
    argv = '--verbose --log_level debug'
    shaft = Shaft(argv=argv)

    g = spawn(shaft.run)
    sleep(0)

    print g

    shaft.kill()

    res = joinall([g])

    print res
