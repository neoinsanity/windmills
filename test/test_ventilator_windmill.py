import time
from test import WindmillTestCase
from test.utils_of_test import gen_archive_output_blueprint_triad
from threading import Thread
from windmills import  DonQuixote


__author__ = 'neoinsanity'


class TestVentilatorWindmill(WindmillTestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_ventilator_default_behavior(self):
        self._executor('test_ventilator_default_behavior')


    def test_ventilator_sub_push_behavior(self):
        self._executor('test_ventilator_sub_push_behavior')


    def _executor(self, test_name=None, stall=None):
        assert test_name

        archive_file, output_file, blueprint = gen_archive_output_blueprint_triad(
            test_name)

        don = DonQuixote(
            file=blueprint,
            disable_keyboard=True)

        t = Thread(target=don.run)
        t.start()
        time.sleep(1)
        assert t.is_alive()
        time.sleep(1)
        if stall:
            time.sleep(stall)
        don.kill()
        t.join(3)
        assert not t.is_alive()

        self.assertFiles(archive_file, output_file)
