#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
from time import ctime


class MT(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name, self.func, self.args = name, func, args

    def get_result(self):
        return self.res

    def run(self):
        self.res = apply(self.func, self.args)

