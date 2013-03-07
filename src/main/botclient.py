import logging

from baseclient import BaseClient

class BotClient(BaseClient):
    def requestAction(self):
        if self.attack():
            return
        
        if self.move():
            return
        
        self.wait()
    
    def move(self):
        for x in range(-1, 1):
            for y in range(-1, 1):
                if x or y:
                    try:
                        self.moveTo(x, y)
                        return True
                    except RuntimeError:
                        pass
        return False
    
    def wait(self):
        # TODO: wait
        pass
    
    def attack(self):
        for x in range(-1, 1):
            for y in range(-1, 1):
                if x or y:
                    t = self.entity.getTile(x, y)
                    monster = t.get('monster')
                    if monster:
                        self.attackEnemy(monster)
                        return True
        return False
    
    def moveTo(self, dx, dy):
        self.doAction('move', {'subject':self.entity, 'dx':dx, 'dy':dy})
    
    def attackEnemy(self, enemy):
        self.doAction('fight', {'subject':self.entity, 'target':enemy})
