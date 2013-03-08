import logging
import traceback
import xml.etree.ElementTree as ET

import baseentity
import tiledmap

class Entity(baseentity.BaseEntity):
    def __init__(self, attrib = {}, alive = False, handler = None):
        self.attrib = attrib
        
        self.alive = alive
        self.setHandler(handler)
        self.dead = False
        
        self.onMap = None
        self.x = None
        self.y = None
        self.position = None
        
        self.watchers = {}
        self.deathWatchers = set()
        
        super().__init__()
    
    def __str__(self):
        # TODO: use plugin instead?..
        try:
            cl = self.attrib['class']
        except KeyError:
            logging.warning('Entity {0} has no class'.format(repr(self)))
            cl = 'unknown object'
        return '{0}'.format(cl)
    
    def __repr__(self):
        return '<Entity: {0} >'.format(self.attrib)
    
    def setHandler(self, handler):
        '''Set handler object which will be requested to action when it's entity's turn'''
        self.handler = handler
    
    def fromXml(xmlEntity):
        '''Create entity from xml'''
        self = Entity()
        self.loadXml(xmlEntity)
        return self
    
    def loadXml(self, xmlEntity):
        '''Load xml into this entity'''
        # TODO: load children
        self.attrib = xmlEntity.attrib
    
    def saveXml(self):
        '''Save entity to xml'''
        # TODO: save children!!
        return ET.Element('entity', self.attrib)
    
    def check(self):
        '''Raise BaseEntityDeadError if entity is already dead'''
        if self.dead:
            raise baseentity.BaseEntityDeadError(self)
    
    def live(self):
        '''One step of entity life'''
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
        '''Destroy this entity'''
        # object cannot be destroyed twice?..
        try:
            self.check()
        except BaseEntityDeadError:
            logging.warning('destroying dead entity')
        
        self.dead = True
        self.funeral()
    
    def watchDeath(self, watcher):
        '''Receive signal when this entity will die'''
        self.deathWatchers.update({watcher})
    
    def funeral(self):
        '''Notify all death watchers'''
        for watcher in self.deathWatchers:
            watcher.attendFuneral(self)
    
    def attr(self, name):
        '''Get entity attribute or None if no attribute'''
        
        self.check()
        
        try:
            return self.attrib[name]
        except KeyError:
            try:
                mlist = worldregistry.world.attrList[name]
            except KeyError:
                pass
            except AttributeError:                      # no world?..
                logging.warning('could not reach modding')
            else:
                # reversed: later added mod has more priority
                # TODO: make explicit priority?
                for mod in reversed(mlist):
                    try:
                        return mod(self)
                    except TypeError:
                        logging.warning('can\'t handle non-function extended attributes')
                    except EntityAttributeError:
                        pass
        return None
    
    def setAttr(self, name, value):
        '''Directly set new attribute value'''
        self.check()
        self.attrib[name] = value
    
    def changeNumericAttr(self, name, delta):
        '''Add delta to some attribute; use this instead of direct attribute set if possible'''
        self.check()
        
        value = float(self.attr(name))
        value += delta
        
        self.attrib[name] = value
        
        self.notifyAttr(name)
    
    def die(self):
        '''Similar to destroy, but available in API; could be handled differently later'''
        self.destroy()
    
    # TODO: separate to Watchable
    def watchAttr(self, target, name):
        '''Notify when attribute is changed'''
        if target in self.watchers:
            self.watchers[target].update({name})
        else:
            self.watchers[target] = {name}
    
    def notifyAttr(self, name):
        for watcher in self.watchers or worldregistry.world.entityWatchers:
            try:
                watchList = self.watchers[watcher]
            except KeyError:
                watchList = worldregistry.world.entityWatchers[watcher]
            if name in watchList:
                watcher.notify(self, name)
    
    def getTile(self, dx = 0, dy = 0):
        '''Get tile on which this entity is placed (default) or offsetted entity'''
        return self.onMap.getTile(self.getX()+dx, self.getY()+dy)
    
    def getPosition(self):
        return self.position
    
    def getCoord(self):
        return self.getX(), self.getY()
    
    def getX(self):
        try:
            self.x+0
        except TypeError:
            logging.warning('entity.x undefined, defaulting to 0')
            self.x = 0
        return self.x
    
    def getY(self):
        try:
            self.y+0
        except TypeError:
            logging.warning('entity.y undefined, defaulting to 0')
            self.y = 0
        return self.y
    
    def getMap(self):
        '''Return map containing this entity'''
        return self.onMap
    
    def mapVision(self):
        # TODO: move to modding
        # TODO: show known map
        
        onMap = self.onMap
        visionMap = tiledmap.TiledMap(onMap.width, onMap.height)
        
        x0 = self.getX()
        y0 = self.getY()
        
        def getTileVision(onMap, visionMap, x, y):
            tile = onMap.getTile(x, y)
            ground = tile.get('ground')
            
            # TODO: copy everything, not just top
            entity = tile.getUpper()
            if entity:
                try:
                    visionMap.getTile(x, y).put(entity.getPosition(), entity)
                except baseentity.PositionTakenError:
                    return False
            
            canSee = not ground.attr('opaque')
            return canSee
        
        def getTileVisionF(onMap, visionMap):
            return lambda x, y: getTileVision(onMap, visionMap, x, y)
        
        onMap.raytrace(x0, y0, getTileVisionF(onMap, visionMap))
        
        return visionMap
    
    def placeOn(self, onMap, x, y, position):
        '''Set this entity to think it's on certain position'''
        self.onMap = onMap
        self.x = x
        self.y = y
        self.position = position
    
    def removeFrom(self, onMap, x, y, position):
        '''Remove from map'''
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
        '''Move object to new coords keeping map and position'''
        oldx = self.x
        oldy = self.y
        oldpos = self.position
        
        # TODO: check movement
        x = self.getX()+dx
        y = self.getY()+dy
        
        try:
            self.onMap.moveTo(self, x, y, self.position)
        except baseentity.PositionTakenError as err:
            self.onMap.moveTo(self, oldx, oldy, oldpos)
            raise err


class EntityPositionError(RuntimeError):
    def __init__(self, entity, problem):
        self.entity = entity
        self.problem = problem

class EntityCoordError(RuntimeError):
    pass

class EntityAttributeError(RuntimeError):
    def __init__(self, entity = None, name = ''):
        self.entity = entity
        self.name = name

class EntityChildPositionError(RuntimeError):
    pass

import worldregistry
