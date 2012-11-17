import logging

from displaying import Displaying
from inputting import Inputting
from mapvisualizer import MapVisualizer
from worldregistry import sysWorldRegistry
from action import Action
import eventlogger

class Client(Displaying, Inputting):
    def __init__(self):
        super().__init__()
        
        self.myTurn = False
        self.quit = False
        self.serverClient = None
        self.mapVisualizer = MapVisualizer()
        self.entity = None
        
        # UI
        self.showingLogs = False
        self.showingInv = False
    
    def connectServer(self, server):
        self.serverClient = server.connect(self)
    
    def askForEntity(self, entity = None):
        try:
            self.serverClient.requestEntity(entity)
        except AttributeError:
            logging.warning('not connected')
    
    def doAction(self, action, args):
        try:
            self.serverClient.request(action, args)
        except AttributeError:
            logging.warning('not connected')
    
    # called from server
    def requestAction(self):
        logging.debug('server requested action')
        self.myTurn = True
    
    # called from server
    def worldChanged(self):
        logging.debug('world changed')
        self.updateDisplay = True
    
    def redraw(self):
        # TODO:
        # - gui
        # - forbid direct access to world
        # - draw vision, not actual map
        # - draw current map
        self.displayData = self.mapVisualizer.toXml(sysWorldRegistry.world.maps[0])
        
        if self.showingLogs:
            self.showLogs()
        
        if self.showingInv:
            self.showInv()
        
        super().redraw()
    
    def showLogs(self):
        # TODO: show full logs
        # TODO: nice output
        self.putString(0, 0, eventlogger.textLog[-1])
    
    def showInv(self):
        inv = self.entity.children
        if not inv:
            # TODO: no constants!
            self.putString(40, 2, 'inventory is empty')
        else:
            # TODO: make this work
            self.putString(40, 2, 'inventory is not empty')
            logging.warning('displaying inventory is not supported yet')
    
    def processKey(self, opcode):
        # TODO: make customizable bindings
        movement = {
            'h' : (-1, 0),
            'j' : (0, 1),
            'k' : (0, -1),
            'l' : (1, 0),
            'y' : (-1, -1),
            'u' : (1, -1),
            'b' : (-1, 1),
            'n' : (1, 1),
        }
        
        ch = chr(opcode)
        
        if ch == 'F':
            action = sysWorldRegistry.world.actions['hit']
            self.doAction(action, {'actor':self.entity, 'tool':self.entity, 'target':self.entity})
        elif ch == 'X':
            action = sysWorldRegistry.world.actions['die']
            self.doAction(action, {'subject':self.entity, 'reason':'user decided to die'})
        elif ch == '!':
            self.showingLogs = not self.showingLogs
        elif ch == 'i':
            self.showingInv = not self.showingInv
        elif ch in movement.keys():
            action = sysWorldRegistry.world.actions['move']
            self.doAction(action, {'subject':self.entity, 'dx':movement[ch][0], 'dy':movement[ch][1]})
        else:
            logging.warning('unhandled key: {0}'.format(chr(opcode)))
