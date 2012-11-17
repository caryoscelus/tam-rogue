import logging

class EntityWrapper:
    # TODO: move api somewhere?..
    entityApi = ['changeNumericAttr', 'attr', 'move', 'die', 'get']
    
    def __init__(self, entity):
        # TODO: eliminate type comparison?..
        if type(entity) == EntityWrapper:
            self.closure = entity.closure
            return
        
        def closure(attrib):
            if attrib in self.entityApi:
                try:
                    return entity.__getattribute__(attrib)
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
