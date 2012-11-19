import os
from threading import Thread
from windmills import CliEmitter, CliListener, EchoService, EmailWindmill
from windmills.lib import Cornerstone


__author__ = 'neoinsanity'

class_map = {
    'CliEmitter': CliEmitter,
    'CliListener': CliListener,
    'Cornerstone': Cornerstone,
    'EchoService': EchoService,
    'EmailWindmill': EmailWindmill,
    }


def thread_wrap_windmill(windmill_name=None, argv=None):
    assert windmill_name
    windmill = class_map[windmill_name](argv=argv)
    t = Thread(target=windmill.run)
    t.windmill = windmill

    return t


def gen_archive_output_pair(test_name=None ):
    archive_file = 'test_data/archive/' + test_name + '._archive'
    output_file = 'test_out/' + test_name + '._output'

    if os.path.exists(output_file):
        os.remove(output_file)

    return archive_file, output_file


def gen_archive_output_blueprint_triad(test_name=None ):
    archive_file, output_file = gen_archive_output_pair(test_name=test_name)

    blueprint = 'test_data/blueprints/' + test_name + '.blueprint'

    return archive_file, output_file, blueprint
