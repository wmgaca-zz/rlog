#!/usr/bin/env python
# coding=utf8

import rlog
import thebar
from baz import Bazooka

def bar():
    hello()

def hello(): pass

def some_main_method():
    print 'Call some_main_method!!!!!'
    thebar.bar_this_shit()

    bar()

if __name__ == '__main__':
    rlog.main()
    some_main_method()
