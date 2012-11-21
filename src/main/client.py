import logging

from displaying import Displaying
from inputting import Inputting, UnknownKeyError
from mapvisualizer import MapVisualizer
from action import Action
import eventlogger
import worldregistry

class Client(Displaying, Inputting):
    MOVEMENT = {
        'h' : (-1, 0),
        'j' : (0, 1),
        'k' : (0, -1),
        'l' : (1, 0),
        'y' : (-1, -1),
        'u' : (1, -1),
        'b' : (-1, 1),
        'n' : (1, 1),
    }
    
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
        
        self.inputState = 'normal'
        self.currentAction = None
        self.actionArgs = None
        self.actionArgsIter = None
        self.actionArgsNext = None
        
        # keymaps
        self.bindings = {}
    
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
        
        if self.inputState == 'normal':
            pass
        elif self.inputState == 'direction':
            self.putString(0, 20, 'direction?')
        elif self.inputState == 'list':
            self.putString(0, 20, 'list element?')
        
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
    
    def bindKeys(self, keys, actionName, args):
        # TODO: specific class?
        action = (actionName, args)
        for key in keys:
            self.bindings[key] = action
    
    def tryLaunchAction(self):
        try:
            self.actionArgsNext = next(self.actionArgsIter)
        except StopIteration:
            # all args are processed, call action now
            self.doAction(self.currentAction, self.actionArgs)
            
            # TODO: move this to come cleaning function
            self.inputState = 'normal'
            self.actionArgsNext = None
            self.actionArgsIter = None
            self.actionArgs = None
            self.currentAction = None
            return True
        return False
    
    def processAction(self):
        '''Try to process current action by replacing obvious arguments'''
        while True:
            argName = self.actionArgsNext
            argType = self.actionArgs[argName]
            if argType == 'entity':
                self.actionArgs[argName] = self.entity
                
                if self.tryLaunchAction():
                    break
            else:
                logging.debug('unknown argType: {0}'.format(argType))
                break
    
    def processKeyBindings(self, opcode):
        if self.inputState == 'normal':
            ch = chr(opcode)
            try:
                actionName, args = self.bindings[ch]
            except KeyError:
                raise UnknownKeyError
            
            self.inputState = 'action'
            self.currentAction = actionName
            self.actionArgs = args
            self.actionArgsIter = iter(args)
            self.actionArgsNext = next(self.actionArgsIter)
            
            self.processAction()
        else:
            argName = self.actionArgsNext
            argType = self.actionArgs[argName]
            if argType == 'direction':
                ch = chr(opcode)
                if ch in self.MOVEMENT:
                    direct = self.MOVEMENT[ch]
                    # TODO: pass normal direction
                    # currently passes integer
                    x = direct[0]
                    y = direct[1]
                    # back formula: x, y = d//3-1, d%3-1
                    d = (x+1)*3+(y+1)
                    self.actionArgs[argName] = d
                    
                    if not self.tryLaunchAction():
                        self.processAction()
                else:
                    raise UnknownKeyError
    
    def processKey(self, opcode):
        # TODO: port everything to moddable bindings
        try:
            self.processKeyBindings(opcode)
        except UnknownKeyError:
            ch = chr(opcode)
            if ch == 'F':
                self.doAction('hit', {'actor':self.entity, 'tool':self.entity, 'target':self.entity})
            elif ch == '!':
                self.showingLogs = not self.showingLogs
            elif ch == 'i':
                self.showingInv = not self.showingInv
            elif ch in self.MOVEMENT:
                self.doAction('move', {'subject':self.entity, 'dx':self.MOVEMENT[ch][0], 'dy':self.MOVEMENT[ch][1]})
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
