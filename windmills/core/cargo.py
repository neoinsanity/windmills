from miller import Miller
from crate import Crate

__author__ = 'neoinsanity'


class Cargo(Miller):
  def __init__(self, handler=None, shaft=None, port=None):
    #: The handler should only be necessary if response expected
    self.handler = handler
    #: The handle to the
    self.shaft = shaft
    self.port = port

  def send(self, crate=None):
    self.shaft.send_crate(cargo=self, crate=crate)

