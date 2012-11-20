import xml.etree.ElementTree as ET
import logging

from mod import Mod
from world import World

class WorldRegistry:
    def __init__(self):
        self.mods = {}
        self.lastMod = 0
        self.world = World()
    
    def loadMod(self, modFile):
        try:
            f = open(modFile)
            modXml = f.read()
            f.close()
            
            newMod = Mod(ET.fromstring(modXml))
            
            self.lastMod += 1
            self.mods[self.lastMod] = newMod
            newMod.applyMod(self.world)
            
            return self.lastMod
        except IOError:
            logging.warning('cannot load mod file {0}'.format(modFile))
        except ET.ParseError:
            logging.warning('cannot parse mod file {0}'.format(modFile))
        return None
    
    def mod(self, modId):
        return self.mods[modId]
    
    def disableMod(self, modId):
        raise NotImplementedError

sysWorldRegistry = WorldRegistry()
