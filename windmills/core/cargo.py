from gevent import spawn

__author__ = 'Raul Gonzalez'


class Cargo(object):
  def __init__(self, delivery_handle=None, port=None):
    #: The handle to the
    self._delivery_handle = delivery_handle

  def send(self, crate=None):
    spawn(self._delivery_handle, crate=crate)

