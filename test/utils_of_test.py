from gevent import sleep, spawn
import os

from windmills.core import Shaft
from windmills.utility_service import CliEmitter, CliListener

__author__ = 'Raul Gonzalez'

class_map = {
  'CliEmitter': CliEmitter,
  'CliListener': CliListener,
  'Shaft': Shaft,
}


def spawn_windmill(windmill_class=None, argv=None):
  assert windmill_class
  windmill = windmill_class(argv=argv)
  the_spawn = spawn(windmill.run)
  sleep(0) # yield so the_spawn can execute

  return the_spawn, windmill


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
