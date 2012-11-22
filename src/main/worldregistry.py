import logging

from world import World
import loader

mods = {}
lastMod = 0
world = World()

def loadMod(modFile):
    newMod = loader.modFromFile(modFile)
    if newMod:
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
