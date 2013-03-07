from sleeping import Sleeping
from entitycontroller import EntityController, EntityControllerMismatchError
import worldregistry

import logging

class ServerClient(Sleeping, EntityController):
    def __init__(self, server, client):
        self.entity = None
        self.actions = []
        self.client = client
        
        # TODO: make it safe
        self.server = server
    
    def register(self):
        # set handler for entity
        self.entity.setHandler(self)
        self.client.entity = self.entity
    
    def assignTo(self, entity):
        self.entity = entity
        self.register()
    
    # to be called on client side
    def request(self, action, args):
        self.actions.append((action, args))
    
    # to be called on client side
    def requestEntity(self, entity = None):
        if entity:
            # TODO: checking
            self.entity = entity
            self.register()
        else:
            raise NotImplementedError('requesting entity to be choosed from server is not supported yet')
    
    # to be called on client side
    def stop(self):
        # TODO: permissions!
        self.server.stop()
    
    def live(self, entity):
        if self.entity != entity:
            raise EntityControllerMismatchError(self.entity, entity)
        
        if self.actions:
            action, args = self.actions.pop(0)
            try:
                # in case action is action name
                action = worldregistry.world.actions[action]
            except KeyError:
                pass
            result = action.applyAction(args)
            self.client.worldChanged()
            if not result:
                # TODO: do something with it
                # maybe just loop over available actions?
                logging.warning('action didn\'t finished successfully')
            return result
        else:
            self.client.requestAction()
            while not self.actions:
                self.sleep()
            return self.live(entity)
    
    def __str__(self):
        return ''
