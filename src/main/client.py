import logging
import copy

from displaying import Displaying
from inputting import Inputting, UnknownKeyError
from mapvisualizer import MapVisualizer
from action import Action
import eventlogger
import worldregistry
import loader

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
        
        self.cleanActionState()
        
        # keymaps
        self.bindings = {}
    
    def cleanActionState(self):
        '''Reset all action inputting variables'''
        self.inputState = 'normal'
        self.currentAction = None
        self.actionArgs = None
        self.actionArgsIter = None
        self.actionArgsNext = None
    
    def loadMod(self, modFile):
        mod = loader.modFromFile(modFile)
        mod.applyMod(self)
    
    # TODO: use default serverClient instead of direct server
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
        self.updateDisplay = True
    
    def redraw(self):
        # TODO:
        # - gui
        # - forbid direct access to world
        # - draw vision, not actual map
        currentMap = self.entity.onMap
        self.displayData = self.mapVisualizer.toXml(currentMap)
        
        # TODO: don't resize on every iteration
        w = currentMap.width
        h = currentMap.height
        self.resize(w+40, h+2)
        
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
        # TODO: make fancy & more universal
        x = 0
        y = 0
        log = eventlogger.eventLog
        stringCount = min(5, len(log))
        for e in log[-stringCount:]:
            self.putString(x, y, str(e))
            y += 1
    
    def showInv(self):
        cnt = self.entity.content
        inv = [v for k, v in cnt.items() if v != None]
        if not inv:
            # TODO: no constants!
            self.putString(20, 2, 'inventory is empty')
        else:
            # TODO: make this work
            self.putString(20, 2, 'inventory is not empty')
            logging.warning('displaying inventory is not supported yet')
    
    def bindKeys(self, keys, actionName, args):
        # TODO: specific class?
        action = (actionName, args)
        for key in keys:
            self.bindings[key] = action
    
    def tryLaunchAction(self):
        '''Get next argument or if it's empty, launch action'''
        try:
            self.actionArgsNext = next(self.actionArgsIter)
        except StopIteration:
            # all args are processed, call action now
            self.doAction(self.currentAction, self.actionArgs)
            
            self.cleanActionState()
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
                break
    
    def processKeyBindings(self, opcode):
        '''Process pressed key according to key bindings'''
        if self.inputState == 'normal':
            ch = chr(opcode)
            try:
                actionName, args = self.bindings[ch]
            except KeyError:
                raise UnknownKeyError
            
            self.inputState = 'action'
            self.currentAction = actionName
            self.actionArgs = copy.deepcopy(args)
            self.actionArgsIter = iter(args)
            
            if not self.tryLaunchAction():
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
            else:
                raise RuntimeError('unknown input type requested: {0}'.format(argType))
    
    def processKey(self, opcode):
        # TODO: port everything to moddable bindings
        try:
            self.processKeyBindings(opcode)
        except UnknownKeyError:
            ch = chr(opcode)
            if ch == '!':
                self.showingLogs = not self.showingLogs
            elif ch == 'i':
                self.showingInv = not self.showingInv
            elif ch in self.MOVEMENT:
                self.doAction('move', {'subject':self.entity, 'dx':self.MOVEMENT[ch][0], 'dy':self.MOVEMENT[ch][1]})
            elif opcode == ord('r')-ord('a')+1:             # CTRL+R
                self.updateDisplay = True
            else:
                logging.warning('unhandled key: {0} ({1})'.format(ch, opcode))
    
    def gameOver(self):
        '''Called when game is considered finished'''
        # TODO: show some exit info, before actual exiting
        self.putString(0, 0, 'game over, thou shall exit now')
        logging.info('game over')
        self.quit = True
        self.serverClient.stop()
        self.notifyDisconnection()
    
    def attendFuneral(self, entity):
        if self.entity == entity:
            self.gameOver()
        else:
            logging.warning('invited to funeral of {0}'.format(entity))
