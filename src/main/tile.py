import copy
import logging
import xml.etree.ElementTree as ET

from entity import Entity, EntityDeadError
from miscerrors import XmlLoadError
import worldregistry

def loadXMLLayers(xml):
    order = []
    content = {}
    emptyContent = {}
    
    for layer in xmlTile:
        if layer.tag == 'layer':
            try:
                name = layer.attrib['name']
                if layer.attrib['type'] == 'object':
                    try:
                        layerContent = Entity.fromXml(layer[0])
                    except IndexError:
                        layerContent = None
                    emptyLayer = None
                elif layer.attrib['type'] == 'list':
                    layerContent = [Entity.fromXml(e) for e in layer]
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

class Tile:
    # order - list: int -> string
    # content - dict: string -> Entity/list
    # if list, it's extandable position
    def __init__(self, content = {}, order = []):
        self.order = order
        self.content = copy.deepcopy(content)
        self.watchers = {}
    
    # TODO: store x/y at tile?..
    def saveXml(self, x, y):
        tileXml = ET.Element('tile', {'x':str(x), 'y':str(y)})
        for name in self.content:
            layer = self.content[name]
            try:
                contentXml = [layer.saveXml()]
                contentType = 'object'
            except AttributeError:
                try:
                    contentXml = [entity.saveXml() for entity in layer]
                    contentType = 'list'
                except TypeError:
                    # just ignore empty layer for size optimization
                    continue
            # not empty here
            layerXml = ET.SubElement(tileXml, 'layer', {'name':name, 'type':contentType})
            layerXml.extend(contentXml)
        return tileXml
    
    def loadXml(self, xmlTile):
        if xmlTile.tag != 'tile':
            raise XmlLoadError(xmlTile)
        
        order, content, emptyContent = loadXMLLayers(xmlTile)
        self.order = order
        self.content = content
        
        worldregistry.world.addTileLayers(emptyContent, order)
    
    def empty(self):
        if not self.content:
            return True
        
        for name in self.content:
            layer = self.content[name]
            if layer:
                return False
        
        return True
    
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
            extPositions = worldregistry.world.layers
            try:
                t = copy.deepcopy(extPositions[position])
                self.content[position] = t
                return t
            except KeyError:
                raise TilePositionError(position)
    
    def getUpper(self):
        '''Get top of the tile "stack"'''
        for position in reversed(self.order):
            try:
                e = self.get(position)
                entity = e[-1]
                entity.check()
                return entity
            except TypeError:                           # on non-lists
                if e != None:
                    return e
            except IndexError:                          # on empty lists
                pass
            except EntityDeadError:                     # found dead entity in list
                self.remove(entity, position)
        return None
    
    def put(self, position, entity):
        '''Put entity onto position; raise error in case it's taken'''
        
        # check if position is ok
        self.get(position)
        
        try:                                            # try list
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
        
        # TODO: proper order
        self.order.append(position)
        
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
                raise TileEntityError(position, entity)
        else:
            content = self.get(position)
            try:                                            # list
                content.remove(entity)
            except ValueError:                              # not in list
                raise TileEntityError(position, entity)
            except AttributeError:                          # entity or empty
                if content != entity:
                    raise TileEntityError(position, entity)
                else:
                    self.content[position] = None
        
        self.notify(position, entity, 'remove')
    
    # is it useful?..
    def isValid(self, position):
        try:
            self.get(position)
            return True
        except TilePositionError:
            return False
    
    def notify(self, position, entity, notification):
        for watcher in self.watchers or worldregistry.world.tileWatchers:
            try:
                watchList = self.watchers[watcher]
            except KeyError:
                watchList = worldregistry.world.tileWatchers[watcher]
            if position in watchList:
                watcher.notify(self, position, notification, entity)
    
    def watchPosition(self, target, name):
        if target in self.watchers:
            self.watchers[target].update({name})
        else:
            self.watchers[target] = {name}

class TileTakenError(RuntimeError):
    def __init__(self, key):
        self.key = key
    
    def __str__(self):
        # TODO: fancy output
        return repr(self.key)

class TilePositionError(RuntimeError):
    def __init__(self, key):
        self.key = key
    
    def __str__(self):
        return 'TilePositionError: {0}'.format(self.key)

class TileEntityError(RuntimeError):
    def __init__(self, position, entity):
        self.position = position
        self.entity = entity
