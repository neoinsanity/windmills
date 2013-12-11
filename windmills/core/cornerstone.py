from brick import Brick

__author__ = 'Raul Gonzalez'


class Cornerstone(object):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.target(*self.args, **self.kwargs)
