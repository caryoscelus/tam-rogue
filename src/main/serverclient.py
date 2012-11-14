from sleeping import Sleeping

class ServerClient(Sleeping):
    def __init__(self, client):
        self.entity = None
        self.actions = []
        self.client = client
    
    def register(self):
        # set handler for entity
        self.entity.handler = self.client
    
    def assignTo(self, entity):
        self.entity = entity
        self.register()
    
    def handle(self):
        self.client.requestAction()
        while not self.actions:
            self.sleep()
        action = self.actions.pop(0)
    
    # to be called on client side
    def request(self, action):
        self.actions.append(action)
    
    def __str__(self):
        return ''
