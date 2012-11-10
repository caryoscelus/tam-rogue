import logging

class Displaying:
    def __init__(self):
        self.updateDisplay = False or True
        self.gfxClient = None
    
    def connectClient(self, gfxClient):
        self.gfxClient = gfxClient
        logging.info('gfx client is on '+str(self.gfxClient))
    
    def redraw(self):
        if self.send(self.displayData):
            self.updateDisplay = False
