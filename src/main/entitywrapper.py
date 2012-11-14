import logging

class EntityWrapper:
    entityApi = ['changeNumericAttr', 'attr']
    
    def __init__(self, entity):
        def closure(attrib):
            if attrib in self.entityApi:
                return entity.__getattribute__(attrib)
            else:
                raise AttributeError(attrib)
        self.closure = closure
    
    def __getattr__(self, attrib):
        logging.debug('entityWrapper: trying to access {0}'.format(attrib))
        return self.closure(attrib)
