import json

__author__ = 'Raul Gonzalez'


class Crate(object):
  def __init__(self, call_ctx=dict(), msg_ctx=dict(), msg_data=None):
    self._call_ctx = call_ctx
    self._msg_ctx = msg_ctx
    self._msg_data = msg_data

    self._dump = None

  @property
  def call_ctx(self):
    return self._call_ctx

  @property
  def msg_ctx(self):
    return self._msg_ctx

  @property
  def msg_data(self):
    return self._msg_data

  @property
  def dump(self):
    if not self._dump:
      self._dump = json.dumps(
        {
          'call_ctx': self.call_ctx,
          'msg_ctx': self.msg_ctx,
          'msg_data': self.msg_data
        })

    return self._dump

  def __str__(self):
    return self.dump
