import logging
import traceback

from miscerrors import XmlLoadError
from entitywrapper import EntityWrapper
from entitywatcher import EntityWatcher
from tilewatcher import TileWatcher
import worldregistry
import eventlogger
import actionapi

# action types:
#   * move
#   * remove
#   * create
#   * change attrib
# action system:
#   * entity handler asks to 
class Action:
    TYPES = {'object', 'integer', 'string', 'arguments'}
    
    def __init__(self):
        self.name = None
        self.arguments = {}
        self.func = None
    
    def fromXml(xml):
        self = Action()
        self.loadXml(xml)
        return self
    
    def loadXml(self, xmlRoot):
        if xmlRoot.tag != 'action':
            raise XmlLoadError(xmlRoot)
        
        self.name = xmlRoot.attrib['name']
        
        args = {}
        
        for node in xmlRoot:
            if node.tag in self.TYPES:
                args[node.attrib['name']] = node.tag
            elif node.tag == 'bindEntity':
                attrib = node.attrib['attrib']
                binding = node.attrib['entity']
                watcher = EntityWatcher(self, binding)
                worldregistry.world.watchAttr(watcher, attrib)
            elif node.tag == 'bindTile':
                position = node.attrib['position']
                # TODO: more proper checking?
                binding = {
                    key : node.attrib[key] for key in node.attrib if not (key in (
                        'position',
                    ))
                }
                watcher = TileWatcher(self, binding)
                worldregistry.world.watchPosition(watcher, position)
            elif node.tag == 'code':
                code = node.text
            else:
                logging.warning('unknown xml node while parsing action: {0}'.format(node))
        
        self.func = self.compileCode(code, args)
    
    def compileCode(self, code, formalArgs):
        ns = {'__builtins__':actionapi}
        compiled = compile(code, '<action mod>', 'exec')
        
        def launchCode(args):
            # TODO: make integer->int, string->str conversion more proper
            def wrapper(args, key):
                try:
                    obj = args[key]
                except KeyError:
                    # put all arguments that are not found in formalArgs
                    return {k:args[k] for k in args if not (k in formalArgs)}
                else:
                    if formalArgs[key] == 'object':
                        return EntityWrapper(obj)
                    elif formalArgs[key] == 'integer' and type(obj) == int:
                        return obj
                    elif formalArgs[key] == 'string' and type(obj) == str:
                        return obj
                    else:
                        raise TypeError('type mismatch')
            
            def defaultValue(argType):
                if argType == 'integer':
                    return 0
                elif argType == 'string':
                    return ''
                elif argType == 'object':
                    return None
                elif argType == 'arguments':
                    return {}
            
            # args that are not present in formalArgs passed
            if set(args.keys()).difference(set(formalArgs.keys())):
                logging.debug(args)
                logging.debug(formalArgs)
                #raise ActionError('undefined args passed')
            wrappers = {}
            wrappers.update({
                key : (defaultValue(formalArgs[key]) or wrapper(args, key)) \
                    for key in formalArgs
            })
            try:
                exec(compiled, ns, wrappers)
            except:
                logging.error('action launching failed')
                logging.debug(traceback.format_exc())
        
        return launchCode
    
    def applyAction(self, args):
        eventlogger.processAction(self, args)
        self.func(args)


class ActionError(RuntimeError):
    pass
