import time
from test.utils_of_test import gen_archive_output_pair
from test.windmill_test_case import WindmillTestCase
from threading import Thread
from windmills.don_quixote import DonQuixote


__author__ = 'neoinsanity'


class TestDonQuixote(WindmillTestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_don_quixote_file(self):
        archive_file, output_file = gen_archive_output_pair(
            'don_quixote_file')

        don = DonQuixote(
            file='test_data/blueprints/don_quixote_file.blueprint',
            disable_keyboard=True)
        assert don

        t = Thread(target=don.run)
        t.start()
        time.sleep(2)
        assert t.is_alive()
        don.kill()
        t.join(3)
        assert not t.is_alive()

        self.assertFiles(archive_file, output_file)


    def test_don_quixote_dictionary(self):
        archive_file, output_file = gen_archive_output_pair(
            'don_quixote_dictionary')

        don = DonQuixote(
            blueprints={"blueprints": [
                {
                    "service": "cli_emitter",
                    "args": "-f "
                            "test_data/inputs/don_quixote_dictionary._input"
                            " --output_sock_url tcp://*:9997 -d 0"
                },
                {
                    "service": "cli_listener",
                    "args": "-f "
                            "test_out/don_quixote_dictionary._output"
                            " --input_sock_url tcp://localhost:9997"
                }
            ]},
            disable_keyboard=True)
        assert don

        t = Thread(target=don.run)
        t.start()
        time.sleep(2)
        assert t.is_alive()
        don.kill()
        t.join(2)
        assert not t.is_alive()

        self.assertFiles(archive_file, output_file)


    def test_don_quixote_blueprint_failure(self):
        # The lack of flie or blueprints argument should raise and exception.
        try:
            don = DonQuixote(disable_keyboard=True)
        except ValueError as e:
            self.assertEqual(e.message,
                              'A blueprint dictionary or file with blueprint '
                              'must be provided.')
            return

        self.fail("An expected ValueError exception was not captured. Test "
                  "failed.")
