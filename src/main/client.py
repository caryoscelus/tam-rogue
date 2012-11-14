import logging

from displaying import Displaying
from inputting import Inputting
from entitycontroller import EntityController
from mapvisualizer import MapVisualizer
from worldregistry import sysWorldRegistry
from action import Action

class Client(Displaying, Inputting, EntityController):
    def __init__(self):
        super().__init__()
        
        self.myTurn = False
        self.quit = False
        self.server = None
        self.mapVisualizer = MapVisualizer()
    
    def live(self, entity):
        super().live(entity)
    
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
            action.applyAction({'actor':self.entity, 'tool':self.entity, 'target':self.entity})
        elif chr(opcode) == 'h':
            action = sysWorldRegistry.world.actions['move']
            action.applyAction({'subject':self.entity, 'dx':-1, 'dy':0})
        elif chr(opcode) == 'j':
            action = sysWorldRegistry.world.actions['move']
            action.applyAction({'subject':self.entity, 'dx':0, 'dy':1})
        elif chr(opcode) == 'k':
            action = sysWorldRegistry.world.actions['move']
            action.applyAction({'subject':self.entity, 'dx':0, 'dy':-1})
        elif chr(opcode) == 'l':
            action = sysWorldRegistry.world.actions['move']
            action.applyAction({'subject':self.entity, 'dx':1, 'dy':0})
        else:
            logging.warning('unhandled key: {0}'.format(chr(opcode)))
