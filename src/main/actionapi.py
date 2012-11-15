# safe builtins
from builtins import Exception, \
                     int, str, dict, list

from logging import debug, info, warning, error

from entity import EntityAttributeError

def action(name, args):
    import worldregistry
    worldregistry.sysWorldRegistry.world.actions[name].applyAction(args)

def traceback():
    import traceback
    debug(traceback.format_exc())
