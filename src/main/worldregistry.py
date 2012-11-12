from mod import Mod
from world import World

class WorldRegistry:
    def __init__(self):
        self.mods = {}
        self.lastMod = 0
        self.world = World()
    
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
    
    def mod(self, modId):
        return self.mods[modId]
    
    def disableMod(self, modId):
        raise NotImplementedError

sysWorldRegistry = WorldRegistry()
