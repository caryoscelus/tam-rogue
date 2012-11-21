import logging

from displaying import Displaying
from inputting import Inputting
from mapvisualizer import MapVisualizer
from action import Action
import eventlogger
import worldregistry

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
    
    def loadMod(self, modFile):
        mod = worldregistry.modFromFile(modFile)
        mod.applyMod(self)
    
    def connectServer(self, server):
        self.serverClient = server.connect(self)
    
    def askForEntity(self, entity = None):
        try:
            self.serverClient.requestEntity(entity)
            self.entity.watchDeath(self)
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
        self.displayData = self.mapVisualizer.toXml(worldregistry.world.maps[0])
        
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
            self.doAction('hit', {'actor':self.entity, 'tool':self.entity, 'target':self.entity})
        elif ch == 'X':
            self.doAction('die', {'subject':self.entity, 'reason':'user decided to die'})
        elif ch == '!':
            self.showingLogs = not self.showingLogs
        elif ch == 'i':
            self.showingInv = not self.showingInv
        elif ch in movement.keys():
            self.doAction('move', {'subject':self.entity, 'dx':movement[ch][0], 'dy':movement[ch][1]})
        elif opcode == ord('r')-ord('a')+1:             # CTRL+R
            logging.debug('manual redraw requested')
        else:
            logging.warning('unhandled key: {0} ({1})'.format(ch, opcode))
        
        # TODO: use some proper method
        self.updateDisplay = True
    
    def gameOver(self):
        self.putString(0, 0, 'game over, thou shall exit now')
        logging.info('game over')
        self.quit = True
        self.serverClient.stop()
    
    def attendFuneral(self, entity):
        if self.entity == entity:
            self.gameOver()
        else:
            logging.warning('invited to funeral of {0}'.format(entity))
