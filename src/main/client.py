import logging

from displaying import Displaying
from inputting import Inputting
from mapvisualizer import MapVisualizer
from worldregistry import sysWorldRegistry
from action import Action

class Client(Displaying, Inputting):
    def __init__(self):
        super().__init__()
        
        self.myTurn = False
        self.quit = False
        self.server = None
        self.mapVisualizer = MapVisualizer()
        
        # TODO: port to some entity controler
        self.entity = None
    
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
    
    def processKey(self, opcode):
        if chr(opcode) == 'F':
            action = sysWorldRegistry.world.actions['hit']
            entity = self.entity
            action.applyAction({'actor':entity, 'tool':entity, 'target':entity})
        elif chr(opcode) == 'h':
            logging.debug('left move action')
            action = sysWorldRegistry.world.actions['move']
            entity = self.entity
            action.applyAction({'subject':entity, 'dx':-1, 'dy':0})
        else:
            logging.warning('unhandled key: {0}'.format(chr(opcode)))
