import logging

from sleeping import Sleeping
from entitywatcher import EntityWatcher

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
    
    def addBinding(self, targetType, event, action, opt, args):
        if targetType == 'entity':
            # TODO: proper bindings, don't just rely on watcher
            binding = None
            for key in args.keys():
                if args[key] == 'target':
                    binding = key
            if event == 'attrib':
                self.watchAttr(EntityWatcher(action, binding), opt['attrib'])
            else:
                logging.warning('addBinding: unknown event {0}'.format(event))
        else:
            logging.warning('addBinding: unknown targetType {0}'.format(targetType))
