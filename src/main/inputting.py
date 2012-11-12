import logging
import threading
import xml.etree.ElementTree as ET

from receiver import Receiver
from starting import Starting

class Inputting(Starting):
    def __init__(self):
        self.receiver = Receiver()
        self.quit = False
        
        self.thread = threading.Thread(None, self.loop, 'inputting')
    
    def connect(self, cl):
        self.receiver.connect(cl)
    
    def start(self):
        super().start()
        self.thread.start()
    
    def loop(self):
        while not self.quit:
            try:
                key = self.readKey()
                self.processKey(key)
            except Exception as err:
                logging.error('error while waiting key')
                logging.debug(err)
    
    def readKey(self):
        key = None
        while not key:
            xml = self.receiver.listen()
            root = ET.fromstring(xml)
            if root.tag == 'input':
                try:
                    key = root.attrib['opcode']
                except Exception as err:
                    logging.warning('bad xml')
            else:
                logging.warning('unknown xml node type')
        return key
    
    def processKey(self, opcode):
        try:
            logging.debug('key pressed: {0}'.format(chr(opcode)))
        except:
            pass
