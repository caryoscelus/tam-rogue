import logging

class EntityWatcher:
    def __init__(self, action, binding):
        self.action = action
        self.binding = binding
    
    def notify(self, entity, name):
        self.action.applyAction({self.binding:entity})
