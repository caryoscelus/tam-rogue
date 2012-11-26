import logging

# TODO: use something like bidict?
_wrappers = {}
_originals = {}

def addWrapper(orig, wrapper):
    _wrappers[orig] = wrapper
    _originals[wrapper] = orig

def orig(wrapper):
    try:
        return _originals[wrapper]
    except KeyError:
        return wrapper

class Wrapper:
    '''Wraps Entity and other objects to forbid random access'''
    
    # TODO: move api somewhere?..
    # TODO: clean up
    entityApi = [
        'changeNumericAttr', 'setAttr', 'attr',
        'move', 'die',
        'get', 'getTile', 'createEntity',
        'getMap', 'getPosition',
        'getCoord', 'getX', 'getY',
        '__getitem__', '__str__',
        'removeFromMap', 'putOn',
        'alive'
    ]
    ignoreTypes = [int, str, float]
    
    def __new__(cls, src):
        # TODO: proper type handling
        if type(src) == Wrapper:
            return src
        if src == None:
            return src
        if type(src) in cls.ignoreTypes:
            return src
        try:
            return _wrappers[src]
        except KeyError:
            newWrapper = super(Wrapper, cls).__new__(cls, src)
            addWrapper(src, newWrapper)
            return newWrapper
    
    def __init__(self, entity):
        if type(entity) == Wrapper:
            self.closure = entity.closure
            return
        
        def closure(attrib):
            if attrib == 'iterable':
                # TODO: make something with it?..
                # this was added because iter(Wrapper) doesn't work for duck typing..
                try:
                    entity.__getitem__
                    result = True
                except AttributeError:
                    result = False
                return lambda: result
            if attrib in self.entityApi:
                try:
                    func = entity.__getattribute__(attrib)
                    def wrappedFunc(*args):
                        args = (orig(arg) for arg in args)
                        result = func(*args)
                        return Wrapper(result)
                    return wrappedFunc
                except AttributeError as err:
                    logging.warning('could not find {0} which is in api'.format(attrib))
                    logging.debug(entity)
                    raise err
            else:
                logging.warning('trying to access {0} throw entity wrapper'.format(attrib))
                raise AttributeError(attrib)
        self.closure = closure
    
    def __getattr__(self, attrib):
        return self.closure(attrib)
    
    def __getitem__(self, *args):
        return self.closure('__getitem__')(*args)
    
    def __str__(self):
        return '<Wrapper around {0}>'.format(self.closure('__str__')())
