import logging
import traceback

# NOTE: should be used multi-pointer friendly
# DO NOT use it in immutable manner
# NOTE: catch EntityDeadError and remove dead links
class Entity:
    def __init__(self, attrib = {}, alive = False, handler = None):
        self.attrib = attrib
        self.children = {}
        
        self.alive = alive
        self.setHandler(handler)
        self.dead = False
        
        self.onMap = None
        self.x = None
        self.y = None
        self.position = None
        
        self.watchers = {}
    
    def __str__(self):
        return '<Entity: {0} >'.format(self.attrib)
    
    def setHandler(self, handler):
        self.handler = handler
    
    # static
    def fromXml(xmlEntity):
        self = Entity()
        self.loadXml(xmlEntity)
        return self
    
    def loadXml(self, xmlEntity):
        self.attrib = xmlEntity.attrib
    
    def check(self):
        if self.dead:
            raise EntityDeadError(self)
    
    def live(self):
        self.check()
        if self.alive:
            try:
                self.handler.live(self)
            except TypeError:
                logging.warning('could not call handler live function')
                logging.debug(traceback.format_exc())
            except AttributeError:
                logging.warning('no handler')
            return True
        
        return False
    
    def destroy(self):
        # object cannot be destroyed twice?..
        try:
            self.check()
        except EntityDeadError:
            logging.warning('destroying dead entity')
        
        self.dead = True
    
    def attr(self, name):
        self.check()
        
        try:
            return self.attrib[name]
        except KeyError:
            try:
                return sysWorldRegistry.world.attrList[name](self)
            except AttributeError:                      # no world?..
                logging.warning('could not reach modding')
                raise EntityAttributeError(self, name)
            except TypeError:
                raise NotImplementedError('can\'t handle non-function extended attributes')
            except KeyError:
                raise EntityAttributeError(self, name)
    
    def changeNumericAttr(self, name, delta):
        self.check()
        
        value = int(self.attr(name))
        value += delta
        
        self.attrib[name] = value
        
        self.notifyAttr(name)
    
    # NOTE: different from destroy -> available in action api
    def die(self):
        self.destroy()
    
    def watchAttr(self, target, name):
        if target in self.watchers:
            self.watchers[target].update({name})
        else:
            self.watchers[target] = {name}
    
    def notifyAttr(self, name):
        for watcher in self.watchers or sysWorldRegistry.world.watchers:
            try:
                watchList = self.watchers[watcher]
            except KeyError:
                watchList = sysWorldRegistry.world.watchers
            if name in watchList:
                watcher.notify(self, name)
    
    def placeOn(self, onMap, x, y, position):
        self.onMap = onMap
        self.x = x
        self.y = y
        self.position = position
    
    def removeFrom(self, onMap, x, y, position):
        if self.onMap != onMap:
            raise EntityPositionError(self, onMap)
        if self.x != x or self.y != y:
            raise EntityPositionError(self, (x, y))
        if self.position != position:
            raise EntityPositionError(self, position)
        self.x = None
        self.y = None
        self.position = None
    
    def move(self, dx, dy):
        # TODO: check movement
        x = self.x+dx
        y = self.y+dy
        
        self.onMap.moveTo(self, x, y, self.position)


class EntityPositionError(RuntimeError):
    def __init__(self, entity, problem):
        self.entity = entity
        self.problem = problem

class EntityDeadError(RuntimeError):
    def __init__(self, entity = None):
        self.entity = entity
    
    #def __str__(self):
        #pass

class EntityAttributeError(RuntimeError):
    def __init__(self, entity = None, name = ''):
        self.entity = entity
        self.name = name

from worldregistry import sysWorldRegistry
