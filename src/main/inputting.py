import logging

class Inputting:
    def __init__(self):
        pass
    
    def processKey(self, opcode):
        try:
            logging.debug('key pressed: {0}'.format(chr(opcode)))
        except:
            pass
