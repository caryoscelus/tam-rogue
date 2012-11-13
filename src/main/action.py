import logging
import traceback

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
    
    def applyAction(self, args):
        self.func(args)
