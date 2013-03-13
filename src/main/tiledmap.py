import xml.etree.ElementTree as ET
import logging
import traceback
import math
import time

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
    
    def raytrace(self, x0, y0, func, limit=None, angle=0, dist=0, wide=None, applyToSelf=True):
        '''Apply func to raytraced coords'''
        
        first = applyToSelf
        if first:
            now = time.time()
        
        if limit == None:
            limit = float('inf')
        
        if applyToSelf:
            if not func(x0, y0):
                return
        
        if not wide:
            wide = 2*math.pi
        
        dist += 1
        if dist >= limit:
            return
        
        points = {}
        
        NUM = int(wide*dist/2)
        if not NUM:
            NUM = 1
        
        nwide = wide/(NUM*2+1)
        
        # iterate possible new angles
        for i in range(-NUM, NUM+1):
            ang = angle+i*nwide
            x = int(x0 + math.cos(ang)*dist)
            y = int(y0 + math.sin(ang)*dist)
            if (x, y) in points:
                oang, n = points[(x, y)]
                nang = (oang*n+ang)/(n+1)
                points[(x, y)] = (nang, n+1)
            else:
                points[(x, y)] = (ang, 1)
        
        for x, y in points:
            if self.checkTile(x, y):
                ang, n = points[(x, y)]
                w = n*nwide
                if func(x, y):
                    self.raytrace(x0, y0, func, limit, ang, dist, w, False)
                else:
                    killedAngle = math.atan(1/2 / dist)
                    if killedAngle < w/2:
                        nw = w/2-killedAngle
                        ad = killedAngle + nw/2
                        self.raytrace(x0, y0, func, limit, ang+ad, dist, nw, False)
                        self.raytrace(x0, y0, func, limit, ang-ad, dist, nw, False)
        
        if first:
            logging.debug('TIME: {0}'.format(time.time()-now))
        return
    
    
    def checkTile(self, x, y):
        '''Check if tile coord are valid'''
        return (x >= 0 and y >= 0) and (x < self.width and y < self.height)
    
    def getTile(self, x, y):
        '''Get tile from position; raise TiledMapSizeError if not on map'''
        if not self.checkTile(x, y):
            raise TiledMapSizeError(self)
        else:
            return self.content[y][x]
    
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
    
    def setContent(self, x, y, position, anEntity):
        '''Force content into position; for use in map generators'''
        anEntity.placeOn(self, x, y, position)
        self.getTile(x, y).set(position, anEntity)
    
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
