import xml.etree.ElementTree as ET
import logging
import traceback

from action import Action

class Mod:
    def __init__(self, xml):
        self.src = ET.fromstring(xml)
        if not self.src.tag == 'mod':
            raise RuntimeError('wrong mod xml')
        self.modType = self.src.attrib['type']
    
    def attrFunc(self, entity, target, source, values):
        try:
            return values[entity.attr(source)]
        except Exception as err:
            logging.debug('while handling attribute mod:')
            logging.debug(err)
            raise EntityAttributeError(entity, source)
    
    def applyMod(self, world):
        if self.modType == 'attrib':
            for group in self.src:
                if group.tag == 'map':
                    source = group.attrib['source']
                    target = group.attrib['target']
                    values = {}
                    for record in group:
                        values[record.get('in')] = record.get('out')
                    world.attrList[target] = lambda entity: self.attrFunc(entity, target, source, values)
                else:
                    raise NotImplementedError('only mapping supported')
        elif self.modType == 'action':
            action = Action.fromXml(self.src)
            world.actions[action.name] = action
        else:
            logging.warning('unknown mod type')
    
    def undoMod(self, world):
        raise NotImplementedError('undo is not supported now')

from entity import EntityAttributeError
