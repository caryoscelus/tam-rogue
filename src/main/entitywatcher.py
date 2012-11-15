import logging

class EntityWatcher:
    def __init__(self):
        pass
    
    def notify(self, entity, name):
        logging.info('entityWatcher was notified about {0} / {1}'.format(entity, name))
