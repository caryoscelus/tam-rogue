class BaseClient:
    # called from server
    def requestAction(self):
        logging.debug('server requested action')
        self.myTurn = True
    
    # called from server
    def worldChanged(self):
        pass
