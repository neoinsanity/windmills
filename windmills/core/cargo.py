from gevent import spawn

__author__ = 'Raul Gonzalez'


class Cargo(object):
  def __init__(self, handler=None, shaft=None, port=None):
    #: The handle to the
    self.shaft = shaft
    self.port = port

  def send(self, crate=None):
    spawn(self.shaft.send_crate, cargo=self, crate=crate)

