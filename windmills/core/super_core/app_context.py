
__author__ = 'Raul Gonzalez'

class AppContext(object):
  def __init__(self):
    self._log = None

  @property
  def log(self):
    return self._log

  @property
  def send_crate(self):
    return self._default
