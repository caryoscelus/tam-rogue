import logging
import traceback
import uuid

from sleeping import Sleeping
from entitywatcher import EntityWatcher
from tiledmap import TiledMap
from entityqueue import EntityQueue, EmptyQueueError

class World(Sleeping):
    def __init__(self):
        self.maps = {}
        self.mapQueue = EntityQueue()
        self.life = self.live()
        
        # modding features
        self.attrList = {}
        self.layers = {}
        self.layerOrder = []
        self.actions = {}
        self.entityWatchers = {}
        self.tileWatchers = {}
        self.mapWatchers = set()
    
    def addTileLayers(self, layers, layerOrder):
        # TODO: check for conflicts
        missing = set(layers.keys()).difference(self.layers.keys())
        for l in layerOrder:
            if l in missing:
                self.layers[l] = layers[l]
                self.layerOrder.append(l)
    
    def setMap(self, mapId, newMap):
        self.maps[mapId] = newMap
        self.mapQueue.push(newMap)
    
    def getMap(self, mapId):
        '''Get map with given id; use this, don't use self.maps direct access'''
        try:
            return self.maps[mapId]
        except KeyError:
            newMap = TiledMap(attrib={'id':mapId})
            self.setMap(mapId, newMap)
            return newMap
    
    def getEmptyMapId(self, sstart = ''):
        '''Get empty id defined by arguments; currently @sstart = begining of id'''
        if isinstance(sstart, str):
            uid = uuid.uuid4().hex
            newId = '{0}{1}'.format(sstart, uid)
            while newId in self.maps:
                logging.warning('uuid repeated!')
                uid = uuid.uuid4().hex
                newId = '{0}{1}'.format(sstart, uid)
            return newId
        else:
            raise NotImplementedError('getEmptyId only implemented for strings now')
    
    def step(self):
        return next(self.life)
    
    def live(self):
        '''Generator-style function yielding map steps'''
        while True:
            try:
                nextMap = self.mapQueue.pop()
            except EmptyQueueError:
                self.mapQueue.reset()
                yield False
            except Exception as err:
                logging.error('Error in World.live():')
                logging.debug(traceback.format_exc())
            else:
                # iterate over objects on map
                while True:
                    t = False
                    try:
                        t = nextMap.step()
                    except Exception as err:
                        logging.error('Error in World.live -> TiledMap.live():')
                        logging.debug(traceback.format_exc())
                    if not t:
                        break
                    yield t
    
    def watch(self, what, watcher, name):
        '''Generic watch function'''
        if watcher in what:
            what[watcher].update({name})
        else:
            what[watcher] = {name}
    
    def watchAttr(self, target, name):
        self.watch(self.entityWatchers, target, name)
    
    def watchPosition(self, target, name):
        self.watch(self.tileWatchers, target, name)
    
    def watchMap(self, target):
        self.mapWatchers.update({target})
    
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
        elif targetType == 'map':
            binding = None
            for key in args.keys():
                if args[key] == 'target':
                    binding = key
            if event == 'empty':
                self.watchMap(EntityWatcher(action, binding))
            else:
                logging.warning('addBinding: unknown map event {0}'.format(event))
        else:
            logging.warning('addBinding: unknown targetType {0}'.format(targetType))
