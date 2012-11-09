import logging
import time

class World:
    def __init__(self):
        #self.entities = []
        self.maps = []
        self.life = self.live()
        
        # modding features
        self.attrList = {}
        self.layers = {}
        self.layerOrder = []
    
    def createMap(self, width, height, attrib = {}):
        newMap = Map(width, height, self.layers, self.layerOrder, attrib)
        self.maps.append(newMap)
    
    def step(self):
        return next(self.life)
    
    def live(self):
        # iterate over time
        while True:
            # iterate over maps
            for tMap in self.maps:
                # iterate over objects on map
                while True:
                    logging.debug('map step')
                    t = tMap.step()
                    if not t:
                        break
                    logging.debug('step done')
                    yield t
                time.sleep(0.1)
