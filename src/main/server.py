import threading

from mod import Mod

# TODO: try eliminating this
globalServer = None

class Server:
    def __init__(self):
        self.clients = []
        self.thread = None
        self.world = None
        self.quit = False
        self.life = None
        self.mods = {}
        self.lastMod = 0
        
        global globalServer
        globalServer = self
    
    def main(self):
        self.life = self.world.live()
        while not self.quit:
            next(life)
    
    def start(self):
        self.thread = threading.Thread(None, self.main, 'world-server', (self,))
        self.thread.start()
    
    def stop(self):
        self.quit = True
    
    def loadMod(self, modFile):
        # TODO: implement
        # should return internal mod id
        f = open(modFile)
        modXml = f.read()
        f.close()
        
        mod = Mod(modXml)
        self.lastMod += 1
        self.mods[self.lastMod] = mod
        mod.applyMod(self.world)
        
        return self.lastMod
    
    def disableMod(self, modId):
        raise NotImplementedError
