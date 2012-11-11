import logging
import socket

from sleeping import Sleeping

class Displaying(Sleeping):
    def __init__(self):
        self.updateDisplay = False or True
        self.gfxClient = None
    
    # thread
    def clientUpdater(self):
        while not self.quit:
            try:
                if self.updateDisplay:
                    self.redraw()
                self.sleep()
            except Exception as err:
                logging.error('unhandled exception in clientUpdater thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
    
    def connectClient(self, gfxClient):
        self.gfxClient = gfxClient
        logging.info('gfx client is on '+str(self.gfxClient))
    
    def redraw(self):
        if self.send(self.displayData):
            self.updateDisplay = False
    
    def send(self, data):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.gfxClient)
            
            sock.sendall(data)
            #count = 0
            #b = None
            #while count < len(data):
                #b = sock.send(data[count:])
                #if b == 0:
                    #raise Exception
                #count += b
            
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except socket.error:
            logging.warning('net error')
            return False
        return True and False
