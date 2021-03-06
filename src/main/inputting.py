import logging
import traceback
import threading
import xml.etree.ElementTree as ET

from receiver import Receiver, ReceiverListeningForbidden, ReceiverTimeoutError
from starting import Starting

class Inputting(Starting, Receiver):
    '''Listens to remote keyboard events'''
    
    def __init__(self):
        super().__init__()
        
        self.quit = False
        
        self.thread = threading.Thread(None, self.loop, 'inputting')
    
    def start(self):
        super().start()
        self.thread.start()
    
    def loop(self):
        while not self.quit:
            try:
                key = self.readKey()
                if key:
                    self.processKey(key)
            except Exception as err:
                logging.error('error while waiting key')
                logging.debug(err)
                logging.debug(traceback.format_exc())
        logging.info('inputting loop() finished')
    
    def readKey(self):
        while not self.quit:
            try:
                xml = self.listen(1)
                root = ET.fromstring(xml)
                if root.tag == 'input':
                    try:
                        key = int(root.attrib['opcode'])
                    except AttributeError:
                        logging.warning('bad xml')
                    else:
                        return key
                else:
                    logging.warning('unknown xml node type')
            except ReceiverListeningForbidden:
                pass
            except ReceiverTimeoutError:
                pass
            except ET.ParseError:
                logging.warning('readKey: received message is unparsable')
                logging.debug(traceback.format_exc())
            except Exception as err:
                logging.error('readKey: unknown exception')
        return None
    
    def processKey(self, opcode):
        try:
            logging.debug('key pressed: {0}'.format(chr(opcode)))
        except Exception as err:
            logging.error(err)


class UnknownKeyError(RuntimeError):
    pass
