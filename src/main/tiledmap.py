from tile import Tile
from entityqueue import EntityQueue, EmptyQueueError
from miscerrors import XmlLoadError

class TiledMap:
    def __init__(self, width = 0, height = 0, layers = {}, layersOrder = [], attrib = {}):
        self.width = width
        self.height = height
        
        self.layers = layers
        self.layersOrder = layersOrder
        
        self.clear()
        self.attrib = attrib
        self.alive = False
        self.queue = EntityQueue()
        self.life = self.live()
    
    def fromXml(xmlRoot):
        self = TiledMap()
        self.loadXml(xmlRoot)
    
    def saveXml(self):
        pass
    
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
                x = int(xmlTile.attrib('x'))
                y = int(xmlTile.get('y'))
            except TypeError:
                raise XmlLoadError(xmlTile)
            
            self.getTile(x, y).loadXml(xmlTile)
    
    def clear(self):
        def t(x, y):
            return Tile(self.layers, self.layersOrder)
        self.content = self.genMap(t) #lambda x, y: Tile(self.layers))
    
    def genMap(self, func):
        if self.width < 0 or self.height < 0:
            raise TiledMapSizeError(self)
        return [[func(x, y) for x in range(self.width)] for y in range(self.height)]
    
    def getTile(self, x, y):
        return self.content[y][x]
    
    def getContent(self, x, y, position):
        return self.getTile(x, y).get(position)
    
    def putOn(self, x, y, position, entity):
        if entity.alive:
            self.queue.push(entity)
        
        tile = self.getTile(x, y)
        tile.put(position, entity)
        entity.placeOn(self, x, y, position)
    
    def removeFromMap(self, entity):
        if entity.alive:
            self.queue.remove(entity)
        
        entity.removeFrom(self, x, y, position)
        #tile = entity.refs.tile
        #tile.remove(entity, entity.refs.position)
    
    def step(self):
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
                except EmptyQueueError:
                    break
                yield entity.live()
            # reload queue
            self.queue.reset()
            yield False


class TiledMapSizeError(RuntimeError):
    def __init__(self, tiledMap):
        self.tiledMap = tiledMap
