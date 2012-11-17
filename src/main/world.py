import logging

from sleeping import Sleeping

class World(Sleeping):
    def __init__(self):
        self.maps = []
        self.life = self.live()
        
        # modding features
        self.attrList = {}
        self.layers = {}
        self.layerOrder = []
        self.actions = {}
        self.entityWatchers = {}
        self.tileWatchers = {}
        self.mapGenerators = {}
    
    def addTileLayers(self, layers, layerOrder):
        # TODO: calculate proper order
        # TODO: check for conflicts
        missing = set(layers.keys()).difference(self.layers.keys())
        for l in missing:
            self.layers[l] = layers[l]
            self.layerOrder.append(l)
    
    # TODO: use
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
                    t = tMap.step()
                    if not t:
                        break
                    yield t
                self.sleep()
    
    def watch(self, what, watcher, name):
        if watcher in what:
            what[watcher].update({name})
        else:
            what[watcher] = {name}
    
    def watchAttr(self, target, name):
        self.watch(self.entityWatchers, target, name)
    
    def watchPosition(self, target, name):
        self.watch(self.tileWatchers, target, name)
