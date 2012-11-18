import xml.etree.ElementTree as ET

from tile import Tile
from entityqueue import EntityQueue, EmptyQueueError
from entity import EntityDeadError
from miscerrors import XmlLoadError
from worldregistry import sysWorldRegistry

class TiledMap:
    def __init__(self, width = 0, height = 0, layers = {}, layersOrder = [], attrib = {}):
        self.width = width
        self.height = height
        
        self.layers = layers
        self.layersOrder = layersOrder
        
        self.clear()
        
        self.attrib = attrib
        self.exist = False
        self.alive = False
        self.queue = EntityQueue()
        self.life = self.live()
    
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
                tile = self.getTile(x, y)
                if not tile.empty():
                    xmlRoot.append(tile.saveXml(x, y))
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
    
    def clear(self):
        def t(x, y):
            return Tile(self.layers, self.layersOrder)
        self.content = self.genMap(t)
    
    def genMap(self, func):
        if self.width < 0 or self.height < 0:
            raise TiledMapSizeError(self)
        return [[func(x, y) for x in range(self.width)] for y in range(self.height)]
    
    def getTile(self, x, y):
        return self.content[y][x]
    
    def getContent(self, x, y, position):
        return self.getTile(x, y).get(position)
    
    def putOn(self, x, y, position, entity, queueChange = True):
        if queueChange and entity.alive:
            self.queue.push(entity)
        
        tile = self.getTile(x, y)
        tile.put(position, entity)
        entity.placeOn(self, x, y, position)
    
    def removeFromMap(self, entity, queueChange = True):
        if queueChange and entity.alive:
            self.queue.remove(entity)
        
        x = entity.x
        y = entity.y
        position = entity.position
        entity.removeFrom(self, x, y, position)
        tile = self.getTile(x, y)
        tile.remove(entity, position)
    
    def moveTo(self, entity, x, y, position):
        self.removeFromMap(entity, queueChange=False)
        self.putOn(x, y, position, entity, queueChange=False)
    
    def step(self):
        if not self.exist:
            # generate map
            if not sysWorldRegistry.world.mapGenerators:
                raise RuntimeError('no map generators')
            else:
                # TODO: choose instead of getting first generator
                generator = next(iter(sysWorldRegistry.world.mapGenerators.values()))
                generator.generate(self)
        if self.alive:
            return next(self.life)
        else:
            return False
    
    def live(self):
        while True:
            # iterate over objects on map
            while True:
                try:
                    entity = self.queue.pop()
                    entity.check()
                except EmptyQueueError:
                    break
                except EntityDeadError:
                    self.removeFromMap(entity)
                else:
                    yield entity.live()
            # reload queue
            self.queue.reset()
            yield False


class TiledMapSizeError(RuntimeError):
    def __init__(self, tiledMap):
        self.tiledMap = tiledMap
