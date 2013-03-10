import logging

from world import World
import loader

mods = {}
lastMod = 0
world = World()

def loadMod(modFile, target = None):
    '''Load mod into worldregistry or target; TODO: remove target loading from here'''
    global world
    target = target or world
    
    newMod = loader.modFromFile(modFile)
    if newMod:
        if target != world:
            newMod.applyMod(target)
            return None
        
        global lastMod
        lastMod += 1
        mods[lastMod] = newMod
        newMod.applyMod(world)
        return lastMod
    else:
        return None

def mod(modId):
    return mods[modId]

def disableMod(modId):
    raise NotImplementedError
