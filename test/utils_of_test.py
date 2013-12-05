from gevent import spawn
import os
from windmills.utility_service.cli_emitter import CliEmitter
from windmills.utility_service.cli_listener import CliListener

__author__ = 'Raul Gonzalez'

class_map = {
  'CliEmitter': CliEmitter,
  'CliListener': CliListener,
}


def thread_wrap_windmill(windmill_name=None, argv=None):
  assert windmill_name
  windmill = class_map[windmill_name](argv=argv)
  t = spawn(target=windmill.run)
  t.windmill = windmill  # a pointer to the created windmill

  return t


def gen_archive(test_name=None):
  return 'test_data/archive/' + test_name + '._archive'


def gen_blueprint(test_name=None):
  return 'test_data/blueprints/' + test_name + '.blueprint'


def gen_input(test_name=None):
  return 'test_data/inputs/' + test_name + '._input'


def gen_output(test_name=None):
  output_file = 'test_out/' + test_name + '._output'

  if os.path.exists(output_file):
    os.remove(output_file)

  return output_file


def gen_archive_output_pair(test_name=None):
  return gen_archive(test_name), gen_output(test_name)


def gen_archive_input_output_triad(test_name=None):
  return gen_archive(test_name), gen_input(test_name), gen_output(test_name)


def gen_archive_output_blueprint_triad(test_name=None):
  return gen_archive(test_name), gen_output(test_name), gen_blueprint(test_name)


def gen_input_output_pair(test_name=None):
  return gen_input(test_name), gen_output(test_name)


def gen_input_output_blueprint_triad(test_name=None):
  return gen_input(test_name), gen_output(test_name), gen_blueprint(test_name)
