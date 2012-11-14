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
        self.serverClient = None
        self.mapVisualizer = MapVisualizer()
        self.entity = None
    
    def live(self, entity):
        if self.entity != entity:
            raise RuntimeError('entity mismatch')
        super().live(entity)
    
    def connectServer(self, server):
        self.serverClient = server.connect(self)
    
    def askForEntity(self, entity = None):
        try:
            self.serverClient.requestEntity(entity)
        except AttributeError:
            logging.warning('not connected')
    
    def doAction(self, action, args):
        action.applyAction(args)
        
        # TODO: make this work or trash it
        try:
            self.serverClient.request(action, args)
        except AttributeError:
            logging.warning('not connected')
    
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
            self.doAction(action, {'actor':self.entity, 'tool':self.entity, 'target':self.entity})
        elif chr(opcode) == 'h':
            action = sysWorldRegistry.world.actions['move']
            self.doAction(action, {'subject':self.entity, 'dx':-1, 'dy':0})
        elif chr(opcode) == 'j':
            action = sysWorldRegistry.world.actions['move']
            self.doAction(action, {'subject':self.entity, 'dx':0, 'dy':1})
        elif chr(opcode) == 'k':
            action = sysWorldRegistry.world.actions['move']
            self.doAction(action, {'subject':self.entity, 'dx':0, 'dy':-1})
        elif chr(opcode) == 'l':
            action = sysWorldRegistry.world.actions['move']
            self.doAction(action, {'subject':self.entity, 'dx':1, 'dy':0})
        else:
            logging.warning('unhandled key: {0}'.format(chr(opcode)))
