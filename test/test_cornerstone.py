from test.windmill_test_case import WindmillTestCase
from test.utils_of_test import thread_wrap_windmill
from time import sleep
from windmills.lib import Cornerstone
from zmq import Context, NOBLOCK, PUB


__author__ = 'neoinsanity'


class TestCornerstone(WindmillTestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_conrnerstone_default_behavior(self):
        foo = Cornerstone()

        t = thread_wrap_windmill('Cornerstone', argv=None)
        t.start()
        assert t.is_alive()

        # send kill command
        kill_cornerstone()
        t.join(3)
        assert not t.is_alive()


def kill_cornerstone():
    context = Context()

    # socket for worker control
    controller = context.socket(PUB)
    controller.bind('tcp://*:7885')

    # give a little time to ensure that the bind occurs
    sleep(1)

    # send the kill command multiple times as clients may miss first attempt
    # due to starting of connection
    controller.send("KILL", NOBLOCK)

    # give it time for zmq to send signal
    sleep(1)

    controller.close()


