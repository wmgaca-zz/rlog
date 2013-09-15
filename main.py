#!/usr/bin/env python
# coding=utf8

import rlog
import thebar
from baz import Bazooka


def bar():
    hello()


def hello():
    rlog.log.info('Create a new Bazooka.')
    b = Bazooka()
    rlog.log.info('K, thanks. Now aim!')
    b.aim()
    rlog.log.info('Fire!!!')
    b.fire()


def some_main_method():
    rlog.log.info('Call some_main_method!')
    thebar.bar_this_shit()
    bar()


if __name__ == '__main__':
    # That's the spot: just call 0-800-RLOG-MAIN and get your
    # logging service immediately!
    rlog.main()

    some_main_method()
