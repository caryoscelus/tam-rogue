import xml.etree.ElementTree as ET
import logging

from mod import Mod
from world import World

mods = {}
lastMod = 0
world = World()

def loadMod(modFile):
    global lastMod
    try:
        f = open(modFile)
        modXml = f.read()
        f.close()
        
        newMod = Mod(ET.fromstring(modXml))
        
        lastMod += 1
        mods[lastMod] = newMod
        newMod.applyMod(world)
        
        return lastMod
    except IOError:
        logging.warning('cannot load mod file {0}'.format(modFile))
    except ET.ParseError:
        logging.warning('cannot parse mod file {0}'.format(modFile))
    return None

def mod(modId):
    return mods[modId]

def disableMod(modId):
    raise NotImplementedError
