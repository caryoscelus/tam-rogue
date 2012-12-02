import logging
import xml.etree.ElementTree as ET

from baseentity import BaseEntity, BaseEntityDeadError, loadXMLLayers
import entity
from miscerrors import XmlLoadError
import worldregistry

class Tile(BaseEntity):
    # order - list: int -> string
    # content - dict: string -> Entity/list
    # if list, it's extandable position
    def __init__(self, content = {}, order = []):
        super().__init__(content, order)
    
    def __str__(self):
        return '<Tile {0}>'.format(super().__str__())
    
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
                    contentXml = [e.saveXml() for e in layer]
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
    
    def getUpper(self):
        '''Get top of the tile "stack"'''
        for position in reversed(self.order):
            try:
                e = self.get(position)
                anEntity = e[-1]
                anEntity.check()
                return anEntity
            except TypeError:                           # on non-lists
                if e != None:
                    e.check()
                    return e
            except IndexError:                          # on empty lists
                pass
            except BaseEntityDeadError:                     # found dead entity in list
                self.remove(anEntity, position)
        return None
    
    # is it useful?..
    def isValid(self, position):
        try:
            self.get(position)
            return True
        except PositionNameError:
            return False
    
    def notify(self, position, anEntity, notification):
        for watcher in self.watchers or worldregistry.world.tileWatchers:
            try:
                watchList = self.watchers[watcher]
            except KeyError:
                watchList = worldregistry.world.tileWatchers[watcher]
            if position in watchList:
                watcher.notify(self, position, notification, anEntity)
    
    def watchPosition(self, target, name):
        if target in self.watchers:
            self.watchers[target].update({name})
        else:
            self.watchers[target] = {name}
