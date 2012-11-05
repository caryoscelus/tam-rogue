from tile import Tile
from entityqueue import EntityQueue, EmptyQueueError

class TiledMap:
    def __init__(self, width, height, layers, layersOrder, attrib = {}):
        self.width = width
        self.height = height
        
        self.layers = layers
        self.layersOrder = layersOrder
        
        self.clear()
        self.attrib = attrib
        self.alive = False
        self.queue = EntityQueue()
    
    def clear(self):
        def t(x, y):
            return Tile(self.layers, self.layersOrder)
        self.content = self.genMap(t) #lambda x, y: Tile(self.layers))
    
    def genMap(self, func):
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
