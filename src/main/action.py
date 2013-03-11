import logging
import traceback
import numbers

from miscerrors import XmlLoadError
from wrapper import Wrapper, orig
from entitywatcher import EntityWatcher
from tilewatcher import TileWatcher
import worldregistry
import eventlogger

# action types:
#   * move
#   * remove
#   * create
#   * change attrib
# action system:
#   * entity handler asks to 
class Action:
    '''Action is action'''
    
    TYPES = {'object', 'integer', 'number', 'string', 'arguments'}
    
    def __init__(self):
        self.name = None
        self.arguments = {}
        self.func = None
        self.attrs = {}
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return str(self)
    
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
            elif node.tag == 'code':
                code = node.text
            elif node.tag == 'attr':
                self.attrs[node.attrib['name']] = node.attrib['value']
            else:
                logging.warning('unknown xml node while parsing action: {0}'.format(node))
        
        self.func = self.compileCode(code, args)
    
    def attr(self, name):
        '''Return attribute'''
        try:
            return self.attrs[name]
        except KeyError:
            return None
    
    def compileCode(self, code, formalArgs):
        '''Comile code (loaded from file) and make laucnhing function'''
        
        import actionapi
        ns = {'__builtins__':actionapi}
        compiled = compile(code, '<action mod>', 'exec')
        
        def launchCode(args):
            '''launch action code, return True if successful'''
            # TODO: make integer->int, string->str conversion more proper
            def wrapperF(args, key):
                try:
                    obj = args[key]
                except KeyError:
                    # put all arguments that are not found in formalArgs
                    return {k:args[k] for k in args if not (k in formalArgs)}
                else:
                    if formalArgs[key] == 'object':
                        return Wrapper(obj)
                    elif formalArgs[key] == 'integer' and type(obj) == int:
                        return obj
                    elif formalArgs[key] == 'number' and isinstance(obj, numbers.Number):
                        return obj
                    elif formalArgs[key] == 'string' and type(obj) == str:
                        return obj
                    else:
                        raise TypeError('type mismatch: requested {0}, found {1}'.format(formalArgs[key], type(obj)))
            
            def defaultValue(argType):
                if argType == 'integer' or argType == 'number':
                    return 0
                elif argType == 'string':
                    return ''
                elif argType == 'object':
                    return None
                elif argType == 'arguments':
                    return {}
            
            wrappers = {}
            wrappers.update({
                key : (defaultValue(formalArgs[key]) or wrapperF(args, key)) \
                    for key in formalArgs
            })
            wrappers.update({
                '_return' : None
            })
            try:
                exec(compiled, ns, wrappers)
                return orig(wrappers['_return'])
            except:
                logging.error('action launching failed')
                logging.debug(traceback.format_exc())
                return False
        
        return launchCode
    
    def applyAction(self, args):
        '''Apply this action'''
        eventlogger.processAction(self, args)
        return self.func(args)


class ActionError(RuntimeError):
    pass
