import logging
import traceback
import xml.etree.ElementTree as ET

import entity
from action import Action
import worldregistry
import baseentity
import loader
from direct import UnDirect

# TODO: use this more generally
def getType(tp):
    if not tp:
        return lambda x: x
    elif tp == 'bool':
        def bb(value):
            try:
                return bool(int(value))
            except ValueError:
                return bool(value)
        return bb
    elif tp == 'int' or tp == 'integer':
        return int
    elif tp == 'float' or tp == 'number':
        return float
    elif tp == 'str' or tp == 'string':
        return str
    else:
        logging.warning('convert: unknown type {0}'.format(tp))
        return lambda x: x

def convert(value, tp):
    '''Convert value to given type'''
    return getType(tp)(value)

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
        if isinstance(values, dict):
            return lambda entity: self.attrFunc(entity, target, source, values)
        else:
            # function
            return lambda entity: values(entity.attr(source))
    
    def applyMod(self, world):
        for node in self.src:
            if node.tag == 'path':
                path = node.attrib['add']
                loader.addPath(path)
            
            elif node.tag == 'require':
                fname = node.attrib['file']
                worldregistry.loadMod(fname, world)
            
            elif node.tag == 'map':
                source = node.attrib['source']
                target = node.attrib['target']
                sType = node.get('source-type')
                tType = node.get('type')
                values = {}
                for record in node:
                    if record.tag == 'value':
                        values[convert(record.get('in'), sType)] = convert(record.get('out'), tType)
                    elif record.tag == 'copy':
                        expr = record.get('value')
                        if not expr or expr == 'value':
                            values = lambda value: value
                            break
                        else:
                            raise NotImplementedError('copying complex values is not supported yet')
                
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
                        args = {}
                        for e in snode:
                            if e.tag == 'arg':
                                value = e.attrib['value']
                                action = e.get('action')                # for list
                                args[e.attrib['name']] = (value, action)
                        bindings = [
                            e.attrib['key'] for e in snode if e.tag == 'bind'
                        ]
                        client.bindKeys(bindings, actionName, args)
                    elif snode.tag == 'movement':
                        try:
                            movement = {
                                snode[i].attrib['key'] : UnDirect(i) \
                                    for i in range(9)
                            }
                        except IndexError:
                            logging.warning('not enough movement keys specified')
                        else:
                            client.movementKeys = movement
                    else:
                        logging.warning('unknown keymap mod xml node tagged "{0}"'.format(snode.tag))
            
            elif node.tag == 'display':
                client = world
                for snode in node:
                    if snode.tag == 'attr':
                        name = snode.attrib['name']
                        tn = snode.get('type')
                        t = getType(tn)
                        client.addDisplayAttribute(name, t)
                    else:
                        logging.warning('unknown display mod xml node tagged "{0}"'.format(snode.tag))
            
            else:
                logging.warning('unknown mod xml node tagged "{0}"'.format(node.tag))
    
    def undoMod(self, world):
        raise NotImplementedError('undo is not supported now')
