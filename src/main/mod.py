import logging
import traceback
import xml.etree.ElementTree as ET

import entity
from action import Action
import worldregistry
import baseentity

# TODO: use this more generally
def convert(value, tp):
    '''Convert value to given type'''
    if not tp:
        return value
    elif tp == 'bool':
        try:
            return bool(int(value))
        except ValueError:
            return bool(value)
    elif tp == 'int':
        return int(value)
    elif tp == 'float':
        return float(value)
    elif tp == 'str':
        return str(value)
    else:
        logging.warning('convert: unknown type {0}'.format(tp))
        return value

class Mod:
    def __init__(self, xml):
        self.src = xml
        if not self.src.tag == 'mod':
            raise RuntimeError('wrong mod xml')
    
    def attrFunc(self, anEntity, target, source, values):
        try:
            return values[anEntity.attr(source)]
        except KeyError:
            raise entity.EntityAttributeError(anEntity, source)
        except Exception as err:
            logging.warning('error while handling attribute mod:')
            logging.debug(traceback.format_exc())
            raise entity.EntityAttributeError(anEntity, source)
    
    def makeAttrFunc(self, target, source, values):
        return lambda entity: self.attrFunc(entity, target, source, values)
    
    def applyMod(self, world):
        for node in self.src:
            if node.tag == 'require':
                fname = node.attrib['file']
                worldregistry.loadMod(fname)
            
            elif node.tag == 'map':
                source = node.attrib['source']
                target = node.attrib['target']
                tp = node.get('type')
                values = {}
                for record in node:
                    values[record.get('in')] = convert(record.get('out'), tp)
                
                if not (target in world.attrList):
                    world.attrList[target] = []
                world.attrList[target].append(self.makeAttrFunc(target, source, values))
            
            elif node.tag == 'layers':
                order, content, emptyContent = baseentity.loadXMLLayers(node)
                worldregistry.world.addTileLayers(content, order)
            
            elif node.tag == 'action':
                action = Action.fromXml(node)
                world.actions[action.name] = action
            
            elif node.tag == 'bind':
                actionName = node.attrib['action']
                targetType = node.attrib['target']
                event = node.attrib['event']
                opt = {key:node.attrib[key] for key in node.attrib.keys() if not (key in (
                    'action', 'target', 'event'
                ))}
                args = {e.tag : e.attrib['value'] for e in node}
                world.addBinding(targetType, event, actionName, opt, args)
            
            elif node.tag == 'keymap':
                client = world
                # TODO: should it be here?
                for snode in node:
                    if snode.tag == 'action':
                        actionName = snode.attrib['name']
                        args = {
                            e.attrib['name']:e.attrib['value'] \
                                for e in snode if e.tag == 'arg'
                        }
                        bindings = [
                            e.attrib['key'] for e in snode if e.tag == 'bind'
                        ]
                        client.bindKeys(bindings, actionName, args)
                    else:
                        logging.warning('unknown keymap mod xml node tagged "{0}"'.format(snode.tag))
            
            else:
                logging.warning('unknown mod xml node tagged "{0}"'.format(node.tag))
    
    def undoMod(self, world):
        raise NotImplementedError('undo is not supported now')
