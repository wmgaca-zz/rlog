import inspect

_DONE = set()
_ACTIVE = False

def main(module='__main__'):
    global _ACTIVE

    explore(module)

    _ACTIVE = True

def explore(module='__main__'):

    if isinstance(module, basestring):
        moduleobj = __import__(module)

        for part in module.split('.')[1:]:
            print 'getattr(%s, %s)' % (moduleobj, part)
            moduleobj = getattr(moduleobj, part)
    else:
        moduleobj = module
        module = moduleobj.__name__

    if moduleobj in _DONE:
        return

    if module.startswith('__') and module != '__main__':
        return

    _DONE.update([moduleobj])
    print '* exploring %s' % module

    print module
    print moduleobj
    print dir(moduleobj)

    for name in dir(moduleobj):
        obj = getattr(moduleobj, name)
        if inspect.ismodule(obj):
            explore(module=obj)
        else:
            decorate_the_sucker(sucker_module=moduleobj, 
                                sucker_object=obj, 
                                sucker_name=name)


def decorate_the_sucker(sucker_module, sucker_object, sucker_name):
    if inspect.isfunction(sucker_object):
        print '+ decorating %s' % sucker_object
        setattr(sucker_module, sucker_name, decor(sucker_object))
    elif inspect.isclass(sucker_object):
        print '+ decorating all methods of %s' % sucker_object
    else:
        print '- nothing to decorate here: %s -> %s' % (sucker_name, type(sucker_object))


def decor(f):
    def wrapper(*args, **kwargs):
        global _ACTIVE

        if not _ACTIVE:
            return f(*args, **kwargs)
        else:
            # TODO check if other functions/methods/classes 
            # in the module decorated?
            print 'CALL %s' % f.__name__
            ret = f(*args, **kwargs)
            print 'END  %s -> %s' % (f.__name__, ret)
            return ret
    return wrapper
