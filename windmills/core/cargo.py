from miller import Miller
from crate import Crate

__author__ = 'neoinsanity'


class Cargo(Miller):
  def __init__(self, handler=None, shaft=None):
    #: The handler should only be necessary if response expected
    self.handler = handler
    #: The handle to the
    self.shaft = shaft

  def send(self, msg_data=None):
    call_ctx = {
      'application': 'chitty,chitty,bang,bang'
    }

    msg_ctx = {
      'msg_type': 'dummy_value'
    }

    crate = Crate(call_ctx=call_ctx, msg_ctx=msg_ctx, msg_data=msg_data)

    self.shaft.send_crate(cargo=self, crate=crate)

