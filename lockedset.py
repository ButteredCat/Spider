#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Lock

def locked_method(method):
    def newmethod(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return newmethod


class LockedSet(set):
    """A set where add() and remove() are thread-saft"""

    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        super(LockedSet, self).__init__(self, *args, **kwargs)

    @locked_method
    def add(self, elem):
        return super(LockedSet, self).add(elem)

    @locked_method
    def remove(self, elem):
        return super(LockedSet, self).remove(elem)

