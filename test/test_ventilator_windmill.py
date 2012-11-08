import time
from test import WindmillTestCase
from test.utils_of_test import gen_archive_output_pair
from threading import Thread
from windmills import  DonQuixote


__author__ = 'neoinsanity'


class TestVentilatorWindmill(WindmillTestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_ventilator_default_behavior(self):
        archive_file, output_file = gen_archive_output_pair(
            'test_ventilator_default_behavior')

        don = DonQuixote(
            file='test_data/blueprints/ventilator_default_behavior.blueprint',
            disable_keyboard=True
        )

        t = Thread(target=don.run)
        t.start()
        time.sleep(2)
        assert t.is_alive()
        don.kill()
        t.join(3)
        assert not t.is_alive()

        self.assertFiles(archive_file, output_file)
