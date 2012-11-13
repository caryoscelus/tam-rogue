import copy

from entity import Entity, EntityDeadError
from miscerrors import XmlLoadError
from worldregistry import sysWorldRegistry

class Tile:
    # order - list: int -> string
    # content - dict: string -> Entity/list
    # if list, it's extandable position
    def __init__(self, content = {}, order = []):
        self.order = order
        self.content = copy.deepcopy(content)
    
    def saveXml(self):
        pass
    
    def loadXml(self, xmlTile):
        if xmlTile.tag != 'tile':
            raise XmlLoadError(xmlTile)
        
        order = []
        content = {}
        
        for layer in xmlTile:
            if layer.tag == 'layer':
                try:
                    name = layer.attrib['name']
                    if layer.attrib['type'] == 'object':
                        try:
                            layerContent = Entity.fromXml(layer[0])
                        except IndexError:
                            layerContent = None
                    elif layer.attrib['type'] == 'list':
                        layerContent = [Entity.fromXml(e) for e in layer]
                    else:
                        logging.warning('unknown xml tile layer type')
                except KeyError:
                    raise XmlLoadError(layer)
                order.append(name)
                content[name] = layerContent
            else:
                logging.warning('unknown xml node type')
        
        self.order = order
        self.content = content
    
    def get(self, position):
        try:
            self.content[position].check()
            return self.content[position]
        except AttributeError:                          # raised on lists
            return self.content[position]
        except EntityDeadError:                         # raised on destroyed object
            self.content[position] = None
            return None
        except KeyError:                                # raised on no position
            extPositions = sysWorldRegistry.world.layers
            try:
                t = copy.deepcopy(extPositions[position])
                self.content[position] = t
                return t
            except KeyError:
                raise TilePositionError(position)
    
    def getUpper(self):
        # no need for modding cause objects cannot be placed in mod positions
        for position in reversed(self.order):
            try:
                e = self.get(position)
                e.check()
                return e
            except AttributeError:                      # on lists
                try:
                    return e[-1]
                except IndexError:                      # on empty lists
                    pass
                except TypeError:                       # on None
                    pass
        return None
    
    def put(self, position, entity):
        # check if position is ok
        self.get(position)
        
        try:
            self.content[position].append(entity)
        except KeyError:
            logging.error('this could not happen!')
            raise TilePositionError(position)
        except AttributeError:                          # non-list
            try:
                self.content[position].check()
                raise TileTakenError(position)
            except AttributeError:                      # raised on non-entity objects (only None is allowed)
                self.content[position] = entity
            except EntityDeadError:                     # raised on destroyed
                self.content[position] = entity
    
    # TODO: position optional
    def remove(self, entity, position):
        content = self.get(position)
        try:
            content.remove(entity)
        except ValueError:                              # not in list
            raise TileEntityError(position, entity)
        except AttributeError:                          # entity or empty
            if content != entity:
                raise TileEntityError(position, entity)
            else:
                self.content[position] = None
    
    # is it useful?..
    def isValid(self, position):
        try:
            self.get(position)
            return True
        except TilePositionError:
            return False

class TileTakenError(RuntimeError):
    def __init__(self, key):
        self.key = key
    
    def __str__(self):
        # TODO: fancy output
        return repr(self.key)

class TilePositionError(RuntimeError):
    def __init__(self, key):
        self.key = key

class TileEntityError(RuntimeError):
    def __init__(self, position, entity):
        self.position = position
        self.entity = entity
