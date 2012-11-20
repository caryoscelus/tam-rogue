import logging
import worldregistry

# TODO: merge with TileWatcher
class EntityWatcher:
    def __init__(self, action, binding):
        self.action = action
        self.binding = binding
    
    def notify(self, entity, name):
        if isinstance(self.action, str):
            self.action = worldregistry.sysWorldRegistry.world.actions[self.action]
        self.action.applyAction({self.binding:entity})
