import logging
import traceback

from miscerrors import XmlLoadError

# action types:
#   * move
#   * remove
#   * create
#   * change attrib
# action system:
#   * entity handler asks to 
class Action:
    def __init__(self):
        # values put here for test
        self.name = 'hit'
        self.arguments = {
            'actor' : True,
            'tool' : True,
            'target' : True,
        }
        def hitFunc(args):
            actor, tool, target = args['actor'], args['tool'], args['target']
            try:
                target.changeNumericAttr('hp', -1)
            except:
                logging.warning('something went wrong in hitFunc')
                logging.debug(traceback.format_exc())
            logging.info('hp: {0}'.format(target.attr('hp')))
        self.func = hitFunc
    
    def fromXml(xml):
        self = Action()
        self.loadXml(xml)
    
    def loadXml(self, xmlRoot):
        if xmlRoot.tag != 'action':
            raise XmlLoadError(xmlRoot)
        
        args = []
        
        for node in xmlRoot:
            if node.tag == 'object':
                # TODO: use filters?..
                args.append(node.attrib('name'))
            elif node.tag == 'code':
                code = node.text
            else:
                logging.warning('unknown xml node while parsing action: {0}'.format(node))
        
        self.func = self.compileCode(code, args)
    
    def compileCode(self, code, args):
        wrappers = dict((key, EntityWrapper(args[key])) for key in args.keys())
        # TODO: add generic function/objects
        ns = {'__builtins__':None}
        compiled = compile(code)
        func = lambda args: exec(compiled, ns, wrappers)
        return func
    
    def applyAction(self, args):
        self.func(args)
