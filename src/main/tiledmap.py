import xml.etree.ElementTree as ET
import logging
import traceback

import tile
from baseentity import PositionEntityError, BaseEntityDeadError
from entityqueue import EntityQueue, EmptyQueueError
import entity
from miscerrors import XmlLoadError
import worldregistry

class TiledMap:
    def __init__(self, width = 0, height = 0, attrib = {}):
        self.width = width
        self.height = height
        
        self.clear()
        
        self.attrib = attrib
        self.exist = False
        self.alive = False
        self.queue = EntityQueue()
        self.life = self.live()
    
    def check(self):
        '''Compatibility with entity.Entity'''
        pass
    
    def setAlive(self, val=True):
        self.alive = val
    
    def attr(self, name):
        # TODO
        return self.attrib[name]
    
    def setAttr(self, name, value):
        self.attrib[name] = value
    
    def fromXml(xmlRoot):
        self = TiledMap()
        self.loadXml(xmlRoot)
        return self
    
    # TODO: separate to loader/saver?..
    # TODO: other formats?
    def saveXml(self):
        xmlRoot = ET.Element('tiledmap', {'width':str(self.width), 'height':str(self.height)})
        for y in range(self.height):
            for x in range(self.width):
                aTile = self.getTile(x, y)
                if not aTile.empty():
                    xmlRoot.append(aTile.saveXml(x, y))
        return xmlRoot
    
    def loadXml(self, xmlRoot):
        if xmlRoot.tag != 'tiledmap':
            raise XmlLoadError(xmlRoot)
        
        try:
            self.width = int(xmlRoot.get('width'))
            self.height = int(xmlRoot.get('height'))
        except TypeError:
            raise XmlLoadError(xmlRoot)
        
        self.clear()
        
        for xmlTile in xmlRoot:
            try:
                x = int(xmlTile.attrib['x'])
                y = int(xmlTile.attrib['y'])
            except TypeError:
                raise XmlLoadError(xmlTile)
            
            self.getTile(x, y).loadXml(xmlTile)
    
    def resize(self, w, h):
        '''Set new map size & clear'''
        self.width = w
        self.height = h
        self.clear()
    
    def clear(self):
        '''Fill map with empty tiles'''
        def t(x, y):
            return tile.Tile(worldregistry.world.layers, worldregistry.world.layerOrder)
        self.content = self.genMap(t)
    
    def setExist(self, value):
        self.exist = value
    
    
    def genMap(self, func):
        '''Generate 2D array generated by func applied to every x, y'''
        if self.width < 0 or self.height < 0:
            raise TiledMapSizeError(self)
        return [[func(x, y) for x in range(self.width)] for y in range(self.height)]
    
    def floodfill(self, x0, y0, func, worked=None):
        '''Apply func to floodfill area'''
        if not worked:
            worked = self.genMap(lambda x, y: False)
        
        todo = [(x0, y0)]
        while todo:
            x, y = todo.pop(0)
            if x < 0 or y < 0:
                continue
            try:
                worked[y][x]
            except IndexError:
                continue
            
            if not worked[y][x]:
                worked[y][x] = True
                if func(x, y):
                    # TODO: optimize
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if dx or dy:
                                todo.append((x+dx, y+dy))
        return worked
    
    def raytrace(self, x0, y0, func, target=None, direct=None, sdir=None, applyToSelf=True, worked=None):
        '''Apply func to raytraced coords'''
        
        # TODO: optimize, it's very slow now
        # probably get rid of recursion
        
        if not worked:
            worked = self.genMap(lambda x, y: False)
        
        try:
            self.getTile(x0, y0)
        except TiledMapSizeError:
            return worked
        
        if worked[y0][x0]:
            return worked
        
        worked[y0][x0] = True
        
        if not target:
            if not applyToSelf or func(x0, y0):
                directs = []
                if not direct:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if dx or dy:
                                directs.append((dx, dy))
                else:
                    dx, dy = direct
                    directs.append((dx, dy))
                    if dx and dy:               # corner
                        directs.append((0, dy))
                        directs.append((dx, 0))
                    elif not dx:
                        directs.append((dy, dy))
                        directs.append((-dy, dy))
                    elif not dy:
                        directs.append((dx, dx))
                        directs.append((dx, -dx))
                    else:
                        raise RuntimeError('(0, 0) direction')
                
                for d in directs:
                    nsdir = sdir
                    dx, dy = d
                    dn = direct or (dx, dy)
                    if direct and direct != (dx, dy):
                        if sdir and sdir != (dx, dy):
                            continue
                        nsdir = (dx, dy)
                        if sdir:
                            direct = sdir
                    worked = self.raytrace(x0+dx, y0+dy, func, direct=dn, sdir=nsdir, worked=worked)
            return worked
        else:
            raise NotImplementedError('No support for targeted raytracing yet')
    
    
    def getTile(self, x, y):
        '''Get tile from position; raise TiledMapSizeError if not on map'''
        if x < 0 or y < 0:
            raise TiledMapSizeError(self)
        try:
            return self.content[y][x]
        except IndexError:
            raise TiledMapSizeError(self)
        except TypeError:
            raise TypeError('getTile() arguments should be integers, got {0}'.format((x, y)))
    
    def getContent(self, x, y, position):
        '''Get content from (x,y)->position'''
        return self.getTile(x, y).get(position)
    
    def putOn(self, x, y, position, anEntity, queueChange = True):
        '''Put anEntity on specified position, including setting this position for entity'''
        if queueChange and anEntity.alive:
            self.queue.push(anEntity)
        
        anEntity.placeOn(self, x, y, position)
        aTile = self.getTile(x, y)
        aTile.put(position, anEntity)
    
    def removeFromMap(self, anEntity, queueChange = True):
        '''Remove entity from map if it's on it'''
        if queueChange and anEntity.alive:
            self.queue.remove(anEntity)
        
        x = anEntity.x
        y = anEntity.y
        
        if x == None or y == None:
            raise entity.EntityCoordError(anEntity)
        
        position = anEntity.position
        anEntity.removeFrom(self, x, y, position)
        aTile = self.getTile(x, y)
        try:
            aTile.remove(anEntity, position)
        except PositionEntityError:
            logging.warning('trying to remove entity from aTile which doesn\'t contain it')
            logging.debug('aTile: {0}, entity: {1}, position: {2}'.format(aTile, anEntity, position))
    
    def moveTo(self, anEntity, x, y, position):
        try:
            self.removeFromMap(anEntity, queueChange=False)
        except entity.EntityCoordError:
            logging.warning('moveTo() called when entity had no position')
        self.putOn(x, y, position, anEntity, queueChange=False)
    
    def createEntity(self, attrib, x, y, position):
        anEntity = entity.Entity(attrib)
        self.putOn(x, y, position, anEntity)
        return anEntity
    
    def step(self):
        '''Do one step of map live'''
        if not self.exist:
            self.notifyEmpty()
            return False
        if self.alive:
            return next(self.life)
        else:
            return False
    
    def notifyEmpty(self):
        '''Notify about map being empty, not generated yet'''
        for watcher in worldregistry.world.mapWatchers:
            watcher.notify(self, 'empty')
    
    def live(self):
        '''Generator-style function yilding entity.live() or False in case of queue reloading'''
        while True:
            try:
                anEntity = self.queue.pop()
                anEntity.check()
            except EmptyQueueError:
                # reload queue
                self.queue.reset()
                yield False
            except BaseEntityDeadError:
                self.removeFromMap(anEntity)
            except Exception as err:
                logging.error('Error in TiledMap.live():')
                logging.debug(traceback.format_exc())
            else:
                try:
                    yield anEntity.live()
                except Exception as err:
                    logging.error('Error in TiledMap.live -> anEntity.live():')
                    logging.debug(traceback.format_exc())


class TiledMapSizeError(RuntimeError):
    def __init__(self, tiledMap):
        self.tiledMap = tiledMap


class TiledMapNotExist(RuntimeError):
    '''Raised when map doesn't existed (generated)'''
    pass
