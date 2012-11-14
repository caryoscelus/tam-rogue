import logging
import traceback

from miscerrors import XmlLoadError
from entitywrapper import EntityWrapper

# action types:
#   * move
#   * remove
#   * create
#   * change attrib
# action system:
#   * entity handler asks to 
class Action:
    def __init__(self):
        self.name = None
        self.arguments = {}
        self.func = None
    
    def fromXml(xml):
        self = Action()
        self.loadXml(xml)
        return self
    
    def loadXml(self, xmlRoot):
        if xmlRoot.tag != 'mod' or xmlRoot.get('type') != 'action':
            raise XmlLoadError(xmlRoot)
        
        self.name = xmlRoot.attrib['name']
        
        args = []
        
        for node in xmlRoot:
            if node.tag == 'object':
                # TODO: use filters?..
                args.append(node.attrib['name'])
            elif node.tag == 'code':
                code = node.text
            else:
                logging.warning('unknown xml node while parsing action: {0}'.format(node))
        
        self.func = self.compileCode(code, args)
    
    def compileCode(self, code, formalArgs):
        # TODO: add safe builtins; check loggin for safety
        safeBuiltins = None #__builtins__
        ns = {'__builtins__':safeBuiltins, 'logging':logging}
        compiled = compile(code, '<action mod>', 'exec')
        
        def launchCode(args):
            # args that are not present in formalArgs passed
            if set(args.keys()).difference(set(formalArgs)):
                raise ActionError('undefined args passed')
            wrappers = dict((key, EntityWrapper(args[key])) for key in args.keys())
            exec(compiled, ns, wrappers)
        
        return launchCode
    
    def applyAction(self, args):
        self.func(args)


class ActionError(RuntimeError):
    pass
