# safe builtins
from builtins import Exception, \
                     int, str, dict, list

from logging import info, warning, error

def action(name, args):
    import worldregistry
    worldregistry.sysWorldRegistry.world.actions[name].applyAction(args)
