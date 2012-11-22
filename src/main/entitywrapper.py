import logging

class EntityWrapper:
    # TODO: move api somewhere?..
    entityApi = ['changeNumericAttr', 'setAttr', 'attr', 'move', 'die', 'get', 'getTile']
    ignoreTypes = [int, str]
    
    def __new__(cls, src):
        # TODO: proper type handling
        if type(src) == EntityWrapper:
            return src
        if src == None:
            return src
        if type(src) in cls.ignoreTypes:
            return src
        return super(EntityWrapper, cls).__new__(cls, src)
    
    def __init__(self, entity):
        if type(entity) == EntityWrapper:
            self.closure = entity.closure
            return
        
        def closure(attrib):
            if attrib in self.entityApi:
                try:
                    func = entity.__getattribute__(attrib)
                    def wrappedFunc(*args):
                        result = func(*args)
                        return EntityWrapper(result)
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
