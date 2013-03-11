# safe & useful builtins
# TODO: full list
from builtins import Exception, TypeError, RuntimeError, IndexError, KeyError, AttributeError, \
                     int, float, bool, str, dict, set, list, tuple, iter, range, \
                     max, min, \
                     __build_class__, super, type

from functools import reduce

from logging import debug, warning, error

# TODO: more random functions; control seeds
from random import random, choice, shuffle

from entity import Entity, EntityAttributeError
from baseentity import PositionTakenError, BaseEntityDeadError, PositionNameError
from entitycontroller import EntityController
from tiledmap import TiledMapSizeError
from direct import Direct, UnDirect
from botcontroller import BotController

from eventlogger import info

import math

def len(self):
    '''Standard len implementation makes much problems when used with wrappers'''
    return self.__len__()

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

def getEmptyMapId(sstart = ''):
    import worldregistry
    return worldregistry.world.getEmptyMapId(sstart)

def traceback():
    import traceback
    debug(traceback.format_exc())


_GLOBALS = {}

def vexport(name, var):
    _GLOBALS[name] = var

def vimport(name):
    try:
        return _GLOBALS[name]
    except KeyError:
        logging.warning('trying to vimport unexported var')
        return None
