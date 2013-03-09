# safe & useful builtins
# TODO: full list
from builtins import Exception, TypeError, RuntimeError, IndexError, KeyError, AttributeError, \
                     int, float, bool, str, dict, list, tuple, iter, range

from functools import reduce

from logging import debug, warning, error

# TODO: more random functions; control seeds
from random import random

from entity import Entity, EntityAttributeError
from baseentity import PositionTakenError, BaseEntityDeadError, PositionNameError
from tiledmap import TiledMapSizeError
from direct import Direct, UnDirect
from botcontroller import BotController

from eventlogger import info

def action(name, args):
    # TODO: proper action launching..
    try:
        import worldregistry
        action = worldregistry.world.actions[name]
    except KeyError:
        warning('unknown action called')
        traceback()
        return False
    else:
        return action.applyAction(args)

def getMap(mapId):
    import worldregistry
    from wrapper import Wrapper
    return Wrapper(worldregistry.world.getMap(mapId))

def traceback():
    import traceback
    debug(traceback.format_exc())


_GLOBALS = {}

def export(name, var):
    _GLOBALS[name] = var
