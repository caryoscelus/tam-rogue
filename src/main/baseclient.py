import logging

from starting import Starting

class BaseClient(Starting):
    '''Generic interface for entity-controlling clients'''
    
    def __init__(self):
        super().__init__()
        
        self.myTurn = False
        self.serverClient = None
        self.entity = None
    
    def requestAction(self):
        '''Called from server when action required'''
        logging.debug('server requested action')
        self.myTurn = True
    
    def worldChanged(self):
        '''Called from server when world is changed'''
        pass
    
    def askForEntity(self, entity = None):
        '''Get entity to control from server'''
        try:
            self.serverClient.requestEntity(entity)
            self.entity.watchDeath(self)
        except AttributeError:
            logging.warning('not connected')
    
    def doAction(self, action, args):
        '''Schedule specified action'''
        try:
            self.serverClient.request(action, args)
        except AttributeError:
            logging.warning('not connected')
    
    # TODO: use default serverClient instead of direct server
    def connectServer(self, server):
        self.serverClient = server.connect(self)
