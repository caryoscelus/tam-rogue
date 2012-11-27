# safe & useful builtins
# TODO: full list
from builtins import Exception, TypeError, RuntimeError, IndexError, KeyError, \
                     int, str, dict, list, iter, range

from logging import debug, info, warning, error

# TODO: more random functions; control seeds
from random import random

from entity import EntityAttributeError, EntityDeadError
from tile import TileTakenError
from tiledmap import TiledMapSizeError

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
