import logging

from entitycontroller import EntityController
from direct import Direct, UnDirect
import actionapi

class BotController(EntityController):
    def __init__(self):
        super().__init__()
    
    def live(self, entity):
        if self.attack(entity):
            logging.info('bot attacks')
            return
        
        if self.move(entity):
            logging.info('bot moves!')
            return
        
        logging.info('bot waits..')
        self.wait(entity)
    
    def move(self, entity):
        '''Try moving'''
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x or y:
                    t = entity.getTile(x, y)
                    if t.get('ground') and t.get('ground').attr('standable'):
                        self.moveTo(entity, x, y)
                        return True
        return False
    
    def wait(self, entity):
        '''Just wait'''
        actionapi.action('wait', {'subject':entity})
    
    def attack(self, entity):
        '''Try to attack'''
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x or y:
                    t = entity.getTile(x, y)
                    monster = t.get('monster')
                    if monster:
                        self.attackEnemy(entity, x, y)
                        return True
        return False
    
    def moveTo(self, entity, dx, dy):
        actionapi.action('move', {'subject':entity, 'dx':dx, 'dy':dy})
    
    def attackEnemy(self, entity, dx, dy):
        actionapi.action('fight', {'subject':entity, 'target':Direct(dx, dy)})
