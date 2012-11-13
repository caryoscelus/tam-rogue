import logging

from displaying import Displaying
from inputting import Inputting
from mapvisualizer import MapVisualizer
from worldregistry import sysWorldRegistry

class Client(Displaying, Inputting):
    def __init__(self):
        super().__init__()
        
        self.myTurn = False
        self.quit = False
        self.server = None
        self.mapVisualizer = MapVisualizer()
    
    def connectServer(self, server):
        self.server = server
    
    # called from server
    def requestAction(self):
        self.myTurn = True
    
    # called from server
    def worldChanged(self):
        #self.updateWorld = True
        self.updateDisplay = True
    
    def redraw(self):
        # TODO:
        # - gui
        # - forbid direct access to world
        # - draw vision, not actual map
        # - draw current map
        self.displayData = self.mapVisualizer.toXml(sysWorldRegistry.world.maps[0])
        # TODO: optimize xml
        super().redraw()
