#!/usr/bin/env python

import sys
from windmills.core.socket_config import DEFAULT_INPUT_SOCKET
from windmills.core.shaft import Shaft

__author__ = 'Raul Gonzalez'


class CliListener(Shaft):
  def __init__(self, **kwargs):
    # setup the initial default configuration
    self.file = None

    Shaft.__init__(self, **kwargs)

    # register to utilize a receive only input handler
    self.blade(handler=self.listener_recv_handler,
               socket_options=DEFAULT_INPUT_SOCKET)
  def configuration_options(self, arg_parser=None):
    assert arg_parser

    arg_parser.add_argument('-f', '--file',
                            help='A file to append incoming messages by line.')

  def configure(self, args=list()):
    assert args

    if self.file is not None:
      self.log.info('Opening file for output: %s', self.file)
      self._file = open(self.file, 'a')

    self.log.info('CliListener configured ...')

  def listener_recv_handler(self, crate=None):
    """
    This method is a replacement for Cornerstone._default_recv_handler.
    It will take an incoming input message and display it to console,
    or it will send the incoming message content to a designated file is
    one is provided.
    """
    assert crate
    if self.file is None:
      sys.stdout.write(crate.dump)
      sys.stdout.write('\n')
      sys.stdout.flush()
    else:
      self._file.write(crate.dump)
      self._file.write('\n')
      self._file.flush()

    the_dump = crate.dump
    the__dump = crate._dump
    str_crate = str(crate)

    self.log.debug('heard: %s', crate)
    return crate.msg_data


if __name__ == '__main__':
  argv = sys.argv
  cli_listener = CliListener(argv=argv)
  cli_listener.run()
