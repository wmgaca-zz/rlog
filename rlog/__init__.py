#!/usr/bin/env python
# coding=utf8

import inspect
import re

from rlog.decorators import Color, footprint
from rlog import log

__all__ = ['main', 'log']

global _DEBUG, _SELF, _DONE, _ACTIVE, _COLOR, _RESTRICTED_NAME_PATTERN

_DEBUG = True
_SELF = __import__(__name__)
_DONE = set()
_ACTIVE = False
_COLOR = False
_RESTRICTED_NAME_PATTERN = re.compile(r'__[a-zA-Z0-9-_]+__')


def trace(message):
    if _DEBUG:
        print message


def set_active(active=True):
    _ACTIVE = active


def set_color(color=False):
    _COLOR = color


def main(module='__main__'):
    """Run this thing to rlog.
    
    :param module module to be scaned and decorated
    :type module basestring or module object
    """

    # Search & decorate
    explore(module=module)
    
    # Activate rlog
    set_active(active=False)

    trace('')

def _get(module='__main__'):
    """Get module object and name.
    
    :param module Module to retrieve
    :type module basestring or module object

    :return Module object and its name
    :rtype tuple
    """

    if isinstance(module, basestring):
        obj = __import__(module)
        for part in module.split('.')[1:]:
            obj = getattr(obj, part)
    elif inspect.ismodule(module):
        obj = module

    return obj, obj.__name__


def explore(module='__main__'):
    module, name = _get(module)
    module_id = id(module)

    # Don't repeat yourself
    if module_id in _DONE:
        return
    
    # Add to lookup history
    _DONE.update([module_id])

    # Don' touch the buildins
    if re.match(_RESTRICTED_NAME_PATTERN, name) and name != '__main__':
        return

    trace('%s exploring %s' % (Color.string('*'), name))
    trace('            %s' % module)

    more = []

    for attr_name in dir(module):
        attr = getattr(module, attr_name)

        if inspect.ismodule(attr):
            more.append(attr)
        elif inspect.isfunction(attr):
            _decorate_function(module, attr_name, attr)
        elif inspect.isclass(attr):
            _decorate_class(module, attr_name, attr)
        else:
            trace('  nothing to do here: %s -> %s' % (attr_name, type(attr)))


def _decorate_function(module, attr_name, attr):
    trace('%s decorating function %s' % (Color.string('+', Color.GREEN), attr_name))

    setattr(module, attr_name, footprint(attr))


def _decorate_class(module, class_name, class_object):
    # TODO(wmgaca): What about nested classes?

    trace('%s decorating all methods of %s' % (Color.string('+', Color.GREEN), class_name))
    
    disable = ['__str__', '__repr__']

    for attr_name in dir(class_object):
        attr = getattr(class_object, attr_name)
        
        if inspect.ismethod(attr) or inspect.isfunction(attr):
            _decorate_function(class_object, attr_name, attr) 
