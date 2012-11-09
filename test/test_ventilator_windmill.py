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
        archive_file, output_file, blueprint = gen_archive_output_blueprint_triad(
            'test_ventilator_default_behavior')

        don = DonQuixote(
            file=blueprint,
            disable_keyboard=True)

        t = Thread(target=don.run)
        t.start()
        time.sleep(1)
        assert t.is_alive()
        time.sleep(1)
        don.kill()
        #time.sleep(30000) #todo: raul - remove this long sleep when testing is done
        t.join(3)
        assert not t.is_alive()

        self.assertFiles(archive_file, output_file)

