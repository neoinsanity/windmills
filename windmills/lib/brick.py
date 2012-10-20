"""Brick is a mix-in that contains functionality to configure input and
output sockets for 0mq device and service patterns.
"""
from lib.cornerstone import Cornerstone


__author__ = 'neoinsanity'
__all__ = ['Brick']


class Brick(Cornerstone):
    """

    """


    def __init__(self, **kwargs):
        Cornerstone.__init__(self, **kwargs)
