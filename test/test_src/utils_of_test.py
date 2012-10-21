import os
from threading import Thread
from windmills import CliListener


__author__ = 'neoinsanity'


def gen_archive_output_pair(test_name=None ):
    archive_file = 'test_data/archive/' + test_name + '._archive'
    output_file = 'test_out/' + test_name + '._output'

    if os.path.exists(output_file):
        os.remove(output_file)

    return archive_file, output_file


def thread_wrapped_cli_listener(argv=None):
    cli_listener = CliListener(argv=argv)
    t = Thread(target=cli_listener.run)
    t.cli_listener = cli_listener

    return t

