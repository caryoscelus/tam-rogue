import logging

# NOTE: should be used multi-pointer friendly
# DO NOT use it in immutable manner
# NOTE: catch EntityDeadError and remove dead links
class Entity:
    def __init__(self, attrib = {}, alive = False, handler = None):
        self.attrib = attrib
        self.children = {}
        
        self.alive = alive
        self.handler = handler
        self.dead = False
    
    def __str__(self):
        # TODO
        return str(self.attrib)
    
    # static
    def fromXml(xmlEntity):
        self = Entity()
        self.loadXml(xmlEntity)
        return self
    
    def loadXml(self, xmlEntity):
        pass
    
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

class EntityDeadError(RuntimeError):
    def __init__(self, entity):
        self.entity = entity
    
    #def __str__(self):
        #pass

class EntityAttributeError(RuntimeError):
    def __init__(self, entity, name):
        self.entity = entity
        self.name = name

from worldregistry import sysWorldRegistry
