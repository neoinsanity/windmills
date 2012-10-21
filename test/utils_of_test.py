import os
from threading import Thread
from windmills import CliEmitter, CliListener, EchoService


__author__ = 'neoinsanity'

class_map = {
    'CliEmitter': CliEmitter,
    'CliListener': CliListener,
    'EchoService': EchoService,
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

