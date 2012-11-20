# safe & useful builtins
# TODO: full list
from builtins import Exception, TypeError, RuntimeError, \
                     int, str, dict, list, iter

from logging import debug, info, warning, error

from entity import EntityAttributeError

def action(name, args):
    import worldregistry
    # TODO: proper action launching..
    try:
        action = worldregistry.sysWorldRegistry.world.actions[name]
    except KeyError:
        warning('unknown action called')
        traceback()
    else:
        action.applyAction(args)

def traceback():
    import traceback
    debug(traceback.format_exc())
