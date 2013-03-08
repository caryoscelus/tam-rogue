import logging

from baseclient import BaseClient

class BotClient(BaseClient):
    def requestAction(self):
        if self.attack():
            logging.info('bot attacks')
            return
        
        if self.move():
            logging.info('bot moves!')
            return
        
        self.wait()
    
    def move(self):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x or y:
                    t = self.entity.getTile(x, y)
                    if t.get('ground') and t.get('ground').attr('standable'):
                        self.moveTo(x, y)
                        return True
        return False
    
    def wait(self):
        self.doAction('wait', {'subject':self.entity})
    
    def attack(self):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x or y:
                    t = self.entity.getTile(x, y)
                    monster = t.get('monster')
                    if monster:
                        self.attackEnemy(x, y)
                        return True
        return False
    
    def moveTo(self, dx, dy):
        self.doAction('move', {'subject':self.entity, 'dx':dx, 'dy':dy})
    
    def attackEnemy(self, dx, dy):
        d = (dx+1)*3+(dy+1)
        self.doAction('fight', {'subject':self.entity, 'target':d})
