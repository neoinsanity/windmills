from gevent import spawn, kill, joinall

__author__ = 'Raul Gonzalez'


class Brick(object):
  def __init__(self, app_ctx, func, *args, **kwargs):
    self.log = log
    self._func = func
    self._args = args
    self._kwargs = kwargs
    self._the_spawn = None

  def start(self):
    if not self._the_spawn:
      self.log.info('Starting brick: %s', self)
      self._the_spawn = spawn(self._func, *self._args, **self._kwargs)
    else:
      self.log.debug('Brick is already running.')

  def stop(self):
    if self._the_spawn:
      if not self._the_spawn.ready():
        kill(self._the_spawn)
        joinall(self._the_spawn, timeout=0.5)
        if not self._the_spawn.ready():
          self.log.info('Brick shutdown failure: %s', self)
        else:
          self._the_spawn = None
    else:
      self.log.info('Brick already shutdown for %s', self)
      return
