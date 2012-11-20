import logging
import traceback
import xml.etree.ElementTree as ET

class Mod:
    def __init__(self, xml):
        self.src = xml
        if not self.src.tag == 'mod':
            raise RuntimeError('wrong mod xml')
        self.modType = self.src.get('type')
    
    def attrFunc(self, entity, target, source, values):
        try:
            return values[entity.attr(source)]
        except Exception as err:
            logging.debug('while handling attribute mod:')
            logging.debug(err)
            raise EntityAttributeError(entity, source)
    
    def applyMod(self, world):
        if self.modType == 'action':
            action = Action.fromXml(self.src)
            world.actions[action.name] = action
        elif self.modType == 'mapGenerator':
            generator = MapGenerator.fromXml(self.src)
            world.mapGenerators[generator.name] = generator
        else:
            # TODO: port everything else here
            for node in self.src:
                if node.tag == 'require':
                    fname = node.attrib['file']
                    worldregistry.sysWorldRegistry.loadMod(fname)
                elif node.tag == 'map':
                    source = node.attrib['source']
                    target = node.attrib['target']
                    values = {}
                    for record in node:
                        values[record.get('in')] = record.get('out')
                    world.attrList[target] = lambda entity: self.attrFunc(entity, target, source, values)
                else:
                    logging.warning('unknown mod xml node tagged "{0}"'.format(node.tag))
    
    def undoMod(self, world):
        raise NotImplementedError('undo is not supported now')

from entity import EntityAttributeError
from action import Action
from mapgenerator import MapGenerator
import worldregistry
