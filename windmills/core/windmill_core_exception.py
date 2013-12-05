
__author__ = 'neoinsanity'

class WindmillException(Exception):
  def __init__(self, msg='None'):
    self.msg = msg
    Exception.__init__(self)
