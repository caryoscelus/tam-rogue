import logging

class EntityWrapper:
    entityApi = ['changeNumericAttr', 'attr', 'move', 'die']
    
    def __init__(self, entity):
        def closure(attrib):
            if attrib in self.entityApi:
                return entity.__getattribute__(attrib)
            else:
                raise AttributeError(attrib)
        self.closure = closure
    
    def __getattr__(self, attrib):
        return self.closure(attrib)
