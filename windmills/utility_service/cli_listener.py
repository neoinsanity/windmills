#!/usr/bin/env python
import sys
from windmills.core.shaft import Shaft

__author__ = 'Raul Gonzalez'


class CliListener(Shaft):
  def __init__(self, **kwargs):
    # setup the initial default configuration
    self.file = None

    Shaft.__init__(self, **kwargs)

    # register to utilize a receive only input handler
    self.declare_blade(handler=self.listener_recv_handler)


  def configuration_options(self, arg_parser=None):
    assert arg_parser

    arg_parser.add_argument('-f', '--file',
                            help='A file to append incoming messages by line.')

  def configure(self, args=list()):
    assert args

    if self.file is not None:
      self._file = open(self.file, 'w')

    self.log.info('CliListener configured ...')

  def listener_recv_handler(self, cargo=None):
    """
    This method is a replacement for Cornerstone._default_recv_handler.
    It will take an incoming input message and display it to console,
    or it will send the incoming message content to a designated file is
    one is provided.
    """
    assert cargo
    self.log.debug('cargo: %s', cargo)
    if self.file is None:
      sys.stdout.write(cargo.msg_data)
      sys.stdout.write('\n')
      sys.stdout.flush()
    else:
      self._file.write(cargo.msg_data)
      self._file.write('\n')
      self._file.flush()

    return cargo.msg_data


if __name__ == '__main__':
  argv = sys.argv
  cli_listener = CliListener(argv=argv)
  cli_listener.run()
