
from rlog import log


class _Weapon(object):

    def __init__(self):
        log.info('Init weapon')


class Bazooka(_Weapon):

    def aim(self):
        log.info('Bazooka aimed at target!')

    def fire(self):
        log.info('Pew. Pew, Pew!')
