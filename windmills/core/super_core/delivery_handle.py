__author__ = 'Raul Gonzalez'


class DeliveryHandler(object):
  def __init__(self, delivery_key=None, send_func=None):
    self._delivery_key = delivery_key
    self._send_func = send_func

  def send_crate(self, crate=None):
    self._send_func(self._delivery_key, crate)
