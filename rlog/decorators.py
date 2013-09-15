#!/usr/bin/env python
# coding=utf-8

import re
import inspect
import types
from . import log

# key: function, value: boolean -- has return statement?
__has_return_statement = {}

# Auto decoration flag
DO_NOT_DECORATE_FLAG = '__do_not_decorate'

class Color(object):

    DEFAULT = '\033[00m'
    PURPLE = '\033[01;34m'
    RED = '\033[01;31m'
    GREEN = '\033[01;32m'

    @classmethod
    def string(cls, string, color=PURPLE):
        return color + string + cls.DEFAULT


def __function_has_ret(function):
    """Checks if function has a return statement.
    :rtype boolean
    """
    if function not in __has_return_statement:
        pattern = re.compile(r'(^| |:)return($| |\()')
        found = filter(pattern.findall, inspect.getsource(function).split('\n'))
        __has_return_statement[function] = len(found) > 0

    return __has_return_statement[function]


def __get_function_params(function, *args, **kwargs):
    """Get a dict of function's parameters names and values.
    :rtype dict
    """

    # Get names and default arguments
    fargspec = inspect.getargspec(function)

    if fargspec.defaults:
        arglist = dict([(name, default)
                        for name, default
                        in zip(fargspec.args, fargspec.defaults)])
    else:
        arglist = dict([(name, None) for name in fargspec.args])

    # Get argument values passed to the function
    unnamed = []
    if args:
        for i, value in enumerate(args):
            try:
                arglist[fargspec.args[i]] = value
            except IndexError:
                unnamed.append(value)
    if kwargs:
        for name, value in kwargs.items():
            arglist[name] = value

    # Create final list of all arguments and their values
    farglist = arglist.items() + [('?', value) for value in unnamed]
    
    return farglist


def __format(value):
    """Format a value to display in the log.
    
    :param value Value to be formatted
    :type value object

    :return Formatted value
    :rtype object
    """
    
    if isinstance(value, basestring):
        value = re.sub(r'\r\n', ' ', value)
        value = re.sub(r'\n', ' ', value)
        value = "'%s'" % value

    return value


def footprint(function):

    # Make sure that passed argument is a function
    fun = inspect.isfunction(function)
    met = inspect.ismethod(function)
    assert fun or met, 'Cannot decorate %s: not a function/method!' % function.__name__

    def function_wrapper(*args, **kwargs):
        # Get function arguments and their values
        farglist = __get_function_params(function, *args, **kwargs)

        # Print the header: what function was called
        # and what argument values were passed

        fargdict = dict(farglist)

        if 'self' in fargdict:
            call_str = 'CALL %s.%s.%s (' % (function.__module__, 
                                            fargdict['self'].__class__.__name__, 
                                            function.__name__)
        elif 'cls' in fargdict:
            call_str = 'CALL %s.%s.%s (' % (function.__module__, 
                                            fargdict['cls'].__name__, 
                                            function.__name__)
        else:
            call_str = 'CALL %s.%s (' % (function.__module__, 
                                         function.__name__)

        if not farglist:
            log.info('%s)' % call_str)
        elif len(farglist) == 1:
            log.info('%s%s = %s)' % (call_str,
                                     farglist[0][0],
                                     __format(farglist[0][1])))
        else:
            indent = ' ' * len(call_str)

            # First parameter
            log.info('%s%s = %s' % (call_str,
                                    farglist[0][0],
                                     __format(farglist[0][1])))

            # [1:-1] parameters
            for name, value in farglist[1:-1]:
                log.info('%s%s = %s' % (indent, name,
                                        __format(value)))

            # Last parameters
            log.info('%s%s = %s)' % (indent,
                                     farglist[-1][0],
                                     __format(farglist[-1][1])))

        log.indent()

        # Invoke the functions
        result = function(*args, **kwargs)

        # Print footer and the return value (if present)
        if __function_has_ret(function):
            log.info('END  %s -> %s' % (function.__name__,
                                        __format(result)))
        else:
            log.info('END  %s' % function.__name__)

        log.unindent()

        # Return function result
        return result

    return function_wrapper


def assert_not_none(function):
    def function_wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        assert result is not None, 'Function %s output is None!' % function.__name__
        return result
    return function_wrapper


def disable_auto_decoration(function):
    setattr(function, DO_NOT_DECORATE_FLAG, True)
    return function


def auto_decoration_enabled(function):
    return inspect.isfunction(function) and not hasattr(function, DO_NOT_DECORATE_FLAG)


class _DecorateAllMethods(type):

    _decorator_name = None
    _disable = []

    def __new__(mcs, name, bases, local):
        assert mcs._decorator_name in globals()

        decorator = globals()[mcs._decorator_name]
        for attr_name, attr_value in local.items():
            if attr_name in mcs._disable:
                continue
            if not auto_decoration_enabled(attr_value):
                continue
            local[attr_name] = decorator(attr_value)

        return super(_DecorateAllMethods, mcs).__new__(mcs, name, bases, local)


class FootprintAllMethods(_DecorateAllMethods):

    _decorator_name = 'footprint'
    _disable = ['__repr__', '__str__']
