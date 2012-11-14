import logging

class EntityController:
    def __init__(self):
        super().__init__()
    
    def live(self, entity):
        logging.debug('entity is alive!')
