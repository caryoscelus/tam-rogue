import logging
import copy

from baseclient import BaseClient
from displaying import Displaying
from inputting import Inputting, UnknownKeyError
from mapvisualizer import MapVisualizer
from action import Action
from direct import Direct
import eventlogger
import worldregistry
import loader

class Client(BaseClient, Displaying, Inputting):
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
        
        self.mapVisualizer = MapVisualizer()
        
        # UI
        self.showingLogs = True
        self.showingInv = False
        self.displayAttrs = []
        
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
    
    def worldChanged(self):
        '''Called from server when world is changed'''
        super().worldChanged()
        self.updateDisplay = True
    
    # OUTPUT
    def redraw(self):
        # TODO:
        # - flexible gui
        # - forbid direct access to world
        # - draw vision, not actual map
        mapVision = self.entity.mapVision()
        self.displayData = self.mapVisualizer.toXml(mapVision, 0, 6)
        
        # TODO: don't resize on every iteration
        w = mapVision.width
        h = mapVision.height
        self.resize(w+40, h+8)
        
        if self.showingLogs:
            self.showLogs()
        
        if self.showingInv:
            self.showInv()
        
        if self.inputState == 'normal':
            pass
        elif self.inputState == 'action' and self.actionArgs[self.actionArgsNext] == 'direction':
            self.putString(0, 0, 'direction?')
        elif self.inputState == 'list':
            self.putString(0, 0, 'list element?')
        
        self.showAttr()
        
        super().redraw()
    
    def showLogs(self):
        # TODO: make fancy & more universal
        x = 0
        y = 0
        log = eventlogger.eventLog
        stringCount = min(5, len(log))
        for e in log[-stringCount:]:
            s = str(e)
            if s:
                self.putString(x, y, s)
                y += 1
    
    def showInv(self):
        cnt = self.entity.content
        inv = [v for k, v in cnt.items() if v != None]
        if not inv:
            # TODO: no constants!
            self.putString(30, 2, 'inventory is empty')
        else:
            self.putString(30, 2, 'inventory:')
            ln = 3
            for obj in inv:
                self.putString(30, ln, str(obj))
                ln += 1
    
    def showAttr(self):
        st = '|'
        for name in self.displayAttrs:
            value = self.entity.attr(name)
            s = ' {0}: {1} |'.format(name, value)
            st += s
        self.putString(0, 5, st)
    
    def addDisplayAttribute(self, name):
        self.displayAttrs.append(name)
    
    # INPUT
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
                # to display "direction?" message
                self.updateDisplay = True
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
                    self.actionArgs[argName] = Direct(*direct)
                    
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
            try:
                ch = chr(opcode)
            except KeyError:
                # TODO: other options should still be checked
                logging.warning('unhandled key: ({0})'.format(opcode))
            else:
                if ch == '!':
                    self.showingLogs = not self.showingLogs
                    self.updateDisplay = True
                elif ch == 'i':
                    self.showingInv = not self.showingInv
                    self.updateDisplay = True
                elif ch in self.MOVEMENT:
                    self.doAction('move', {'subject':self.entity, 'dx':self.MOVEMENT[ch][0], 'dy':self.MOVEMENT[ch][1]})
                elif opcode == ord('r')-ord('a')+1:             # CTRL+R
                    self.updateDisplay = True
                elif ch == 'S':
                    self.doQuit()
                else:
                    logging.warning('unhandled key: {0} ({1})'.format(ch, opcode))
    
    def gameOver(self):
        '''Called when game is considered finished'''
        eventlogger.logString('game over, thou shall exit now')
        logging.info('game over')
        self.serverClient.stop()
    
    def doQuit(self):
        '''Actually quit'''
        self.serverClient.stop()
        self.notifyDisconnection()
        self.quit = True
    
    def attendFuneral(self, entity):
        if self.entity == entity:
            self.gameOver()
        else:
            logging.warning('invited to funeral of {0}'.format(entity))
