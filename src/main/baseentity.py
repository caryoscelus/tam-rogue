# NOTE: should be used multi-pointer friendly
# DO NOT use it in immutable manner
# NOTE: catch BaseEntityDeadError and remove dead links
class BaseEntity:
    '''Basic class for entity, tile, etc. Containes attributes & children handling'''
    
    def __init__(self):
        pass
    
    def get(self, position):
        try:
            self.content[position].check()
            return self.content[position]
        except AttributeError:                          # raised on lists
            return self.content[position]
        except BaseEntityDeadError:                         # raised on destroyed object
            self.content[position] = None
            return None
        except KeyError:                                # raised on no position
            extPositions = worldregistry.world.layers
            try:
                t = copy.deepcopy(extPositions[position])
                self.content[position] = t
                return t
            except KeyError:
                raise PositionNameError(position)
    
    def put(self, position, entity):
        '''Put entity onto position; raise error in case it's taken'''
        
        # check if position is ok
        self.get(position)
        
        try:                                            # try list
            self.content[position].append(entity)
        except KeyError:
            logging.error('this could not happen!')
            raise PositionNameError(position)
        except AttributeError:                          # non-list
            try:
                self.content[position].check()
                raise PositionTakenError(position)
            except AttributeError:                      # raised on non-entity objects (only None is allowed)
                self.content[position] = entity
            except BaseEntityDeadError:                     # raised on destroyed
                self.content[position] = entity
        
        self.notify(position, entity, 'add')
    
    def remove(self, entity, position = None):
        '''Remove entity from this tile; raise error if it's not present here'''
        if not position:
            for pos in self.content:
                try:                                    # list
                    self.content[pos].remove(entity)
                    return
                except ValueError:                      # not in list
                    break
                except AttributeError:                  # entity or empty
                    if self.content[pos] == entity:
                        self.content[pos] = None
                        break
            else:
                raise PositionEntityError(position, entity)
        else:
            content = self.get(position)
            try:                                            # list
                content.remove(entity)
            except ValueError:                              # not in list
                raise PositionEntityError(position, entity)
            except AttributeError:                          # entity or empty
                if content != entity:
                    raise PositionEntityError(position, entity)
                else:
                    self.content[position] = None
        
        self.notify(position, entity, 'remove')

class PositionTakenError(RuntimeError):
    def __init__(self, key):
        self.key = key
    
    def __str__(self):
        # TODO: fancy output
        return repr(self.key)

class PositionNameError(RuntimeError):
    def __init__(self, key):
        self.key = key
    
    def __str__(self):
        return 'PositionNameError: {0}'.format(self.key)

class PositionEntityError(RuntimeError):
    def __init__(self, position, entity):
        self.position = position
        self.entity = entity

class BaseEntityDeadError(RuntimeError):
    '''Raised when link to dead entity is used'''
    def __init__(self, entity = None):
        self.entity = entity
    
    def __str__(self):
        return '<BaseEntityDeadError: {0}>'.format(self.entity)

