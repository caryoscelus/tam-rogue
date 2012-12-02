import copy
import logging

# TODO: remove this dependency
import entity

def loadXMLLayers(xml):
    order = []
    content = {}
    emptyContent = {}
    
    for layer in xml:
        if layer.tag == 'layer':
            try:
                name = layer.attrib['name']
                if layer.attrib['type'] == 'object':
                    try:
                        layerContent = entity.Entity.fromXml(layer[0])
                    except IndexError:
                        layerContent = None
                    emptyLayer = None
                elif layer.attrib['type'] == 'list':
                    layerContent = [entity.Entity.fromXml(e) for e in layer]
                    emptyLayer = []
                else:
                    logging.warning('unknown xml tile layer type')
            except KeyError:
                raise XmlLoadError(layer)
            order.append(name)
            content[name] = layerContent
            emptyContent[name] = emptyLayer
        else:
            logging.warning('unknown xml node type')
    
    return order, content, emptyContent


# NOTE: should be used multi-pointer friendly
# DO NOT use it in immutable manner
# NOTE: catch BaseEntityDeadError and remove dead links
class BaseEntity:
    '''Basic class for entity, tile, etc. Containes attributes & children handling'''
    
    def __init__(self, content = {}, order = []):
        self.order = order
        self.content = copy.deepcopy(content)
        self.watchers = {}
    
    def __str__(self):
        return '<BaseEntity {0}>'.format(self.content)
    
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
    
    def put(self, position, anEntity):
        '''Put anEntity onto position; raise error in case it's taken'''
        
        # check if position is ok
        self.get(position)
        
        try:                                            # try list
            self.content[position].append(anEntity)
        except KeyError:
            logging.error('this could not happen!')
            raise PositionNameError(position)
        except AttributeError:                          # non-list
            try:
                self.content[position].check()
                raise PositionTakenError(position)
            except AttributeError:                      # raised on non-anEntity objects (only None is allowed)
                self.content[position] = anEntity
            except BaseEntityDeadError:                     # raised on destroyed
                self.content[position] = anEntity
        
        self.notify(position, anEntity, 'add')
    
    def remove(self, anEntity, position = None):
        '''Remove anEntity from this tile; raise error if it's not present here'''
        if not position:
            for pos in self.content:
                try:                                    # list
                    self.content[pos].remove(anEntity)
                    break
                except ValueError:                      # not in list
                    pass
                except AttributeError:                  # anEntity or empty
                    if self.content[pos] == anEntity:
                        self.content[pos] = None
                        break
            else:
                raise PositionEntityError(position, anEntity)
        else:
            content = self.get(position)
            try:
                iter(content)
                content.remove(anEntity)
            except ValueError:                              # not in list
                raise PositionEntityError(position, anEntity)
            except TypeError:                          # anEntity or empty
                if content != anEntity:
                    raise PositionEntityError(position, anEntity)
                else:
                    self.content[position] = None
        
        self.notify(position, anEntity, 'remove')
    
    def notify(self, position, anEntity, event):
        logging.warning('BaseEntity was notified')

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
    def __init__(self, position, anEntity):
        self.position = position
        self.anEntity = anEntity

class BaseEntityDeadError(RuntimeError):
    '''Raised when link to dead anEntity is used'''
    def __init__(self, anEntity = None):
        self.anEntity = anEntity
    
    def __str__(self):
        return '<BaseEntityDeadError: {0}>'.format(self.anEntity)

import worldregistry
