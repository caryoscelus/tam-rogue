from mod import Mod

class ModRegistry:
    def __init__(self):
        self.mods = {}
        self.lastMod = 0
    
    def loadMod(self, modFile):
        # TODO: implement
        # should return internal mod id
        f = open(modFile)
        modXml = f.read()
        f.close()
        
        mod = Mod(modXml)
        self.lastMod += 1
        self.mods[self.lastMod] = mod
        
        return self.lastMod
    
    def mod(self, modId):
        return self.mods[modId]
    
    def disableMod(self, modId):
        raise NotImplementedError

sysModRegistry = ModRegistry()
