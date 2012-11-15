import logging

# TODO: merge with entity watcher
class TileWatcher:
    def __init__(self, action, binding):
        self.action = action
        self.binding = binding
    
    def notify(self, tile, position, notifyType, entity):
        t = {'tile':tile, 'tileEntity':entity, 'notify':notifyType}
        args = {self.binding[name] : t[name] for name in self.binding}
        self.action.applyAction(args)
