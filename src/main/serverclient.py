from sleeping import Sleeping
from entitycontroller import EntityController

class ServerClient(Sleeping, EntityController):
    def __init__(self, server, client):
        self.entity = None
        self.actions = []
        self.client = client
        
        # TODO: make it safe
        self.server = server
    
    def register(self):
        # set handler for entity
        self.entity.handler = self
        self.client.entity = self.entity
    
    def assignTo(self, entity):
        self.entity = entity
        self.register()
    
    def handle(self):
        self.client.requestAction()
        while not self.actions:
            self.sleep()
        action = self.actions.pop(0)
    
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
    
    def live(self, entity):
        if self.entity != entity:
            raise RuntimeError('entity mismatch')
        super().live(entity)
        # TODO: make something working here
    
    def __str__(self):
        return ''
