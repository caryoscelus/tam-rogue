import logging
import copy

from baseclient import BaseClient
from displaying import Displaying
from inputting import Inputting, UnknownKeyError
from mapvisualizer import MapVisualizer
from action import Action
from direct import Direct
from baseentity import BaseEntityDeadError
import eventlogger
import worldregistry
import loader
import actionapi

class Client(BaseClient, Displaying, Inputting):
    def __init__(self):
        super().__init__()
        
        self.mapVisualizer = MapVisualizer()
        
        # UI
        self.showingLogs = True
        self.showingInv = False
        self.showingList = False
        self.currentList = None
        self.displayAttrs = []
        
        self.cleanActionState()
        
        # keymaps
        self.movementKeys = {
            'h' : (-1, 0),
            'j' : (0, 1),
            'k' : (0, -1),
            'l' : (1, 0),
            'y' : (-1, -1),
            'u' : (1, -1),
            'b' : (-1, 1),
            'n' : (1, 1),
            }
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
        try:
            mod.applyMod(self)
        except AttributeError:
            logging.warning('client can\'t load mod')
    
    def worldChanged(self):
        '''Called from server when world is changed'''
        super().worldChanged()
        self.updateDisplay = True
    
    def askForEntity(self, entity = None):
        super().askForEntity(entity)
        if entity:
            entity.setAttr('control', 'player')
    
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
        
        if self.inputState == 'normal':
            pass
        elif self.inputState == 'action' and self.nextArgumentType() == 'direction':
            self.putString(0, 0, 'direction?  ')
        elif self.inputState == 'action' and self.nextArgumentType() == 'inventory':
            self.showingInv = True
            self.putString(0, 0, 'list element?  ')
        elif self.inputState == 'action' and self.nextArgumentType() == 'list':
            self.showingList = True
            self.currentList = actionapi.action(self.nextArgument()[1], {'subject':self.entity})
            self.putString(0, 0, 'list element?  ')
        
        if self.showingInv:
            self.showInv()
        
        if self.showingList and self.currentList:
            self.showList(self.currentList)
        
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
        inv = self.entity.get('inv')
        if not inv:
            # TODO: no constants!
            self.putString(30, 0, 'inventory is empty')
        else:
            self.putString(30, 0, 'inventory:')
            self.showList(inv)
    
    def showList(self, entityList):
        ln = 1
        for i in range(len(entityList)):
            self.putString(30, ln+i, '{0}: {1}'.format(i, entityList[i]))
    
    def showAttr(self):
        st = '|'
        for name, t in self.displayAttrs:
            try:
                value = self.entity.attr(name)
            except BaseEntityDeadError:
                logging.warning('entity died')
                return
            s = ' {0}: {1} |'.format(name, t(value))
            st += s
        self.putString(0, 5, st)
    
    def addDisplayAttribute(self, name, t):
        self.displayAttrs.append((name, t))
    
    # INPUT
    def bindKeys(self, keys, actionName, args):
        '''Bind list of key to do action'''
        action = (actionName, args)
        for key in keys:
            self.bindings[key] = action
    
    def nextArgument(self):
        '''Return representation of next argument'''
        return self.actionArgs[self.actionArgsNext]
    
    def nextArgumentType(self):
        '''Return type of next argument'''
        return self.nextArgument()[0]
    
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
            argType = self.actionArgs[argName][0]
            if argType == 'entity':
                self.actionArgs[argName] = self.entity
                
                if self.tryLaunchAction():
                    break
            else:
                # to display "direction?" message
                self.updateDisplay = True
                break
    
    def processListArgument(self, elist, opcode):
        '''Fill in list argument, returning it'''
        ch = chr(opcode)
        if ch == '-':
            arg = None
        else:
            try:
                num = int(ch)
                arg = elist[num]
            except ValueError:
                raise UnknownKeyError
            except IndexError:
                raise UnknownKeyError
        return arg
    
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
            arg = self.actionArgs[argName]
            argType = arg[0]
            if argType == 'direction':
                ch = chr(opcode)
                if ch in self.movementKeys:
                    direct = self.movementKeys[ch]
                    result = Direct(*direct)
                else:
                    raise UnknownKeyError
            elif argType == 'inventory':
                result = self.processListArgument(self.entity.get('inv'), opcode)
            elif argType == 'list':
                elist = actionapi.action(arg[1], {'subject':self.entity})
                result = self.processListArgument(elist, opcode)
            else:
                raise RuntimeError('unknown input type requested: {0}'.format(argType))
            
            self.actionArgs[argName] = result
            if not self.tryLaunchAction():
                self.processAction()
    
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
                if self.inputState == 'normal':
                    if ch == '!':
                        self.showingLogs = not self.showingLogs
                        self.updateDisplay = True
                    elif ch == 'i':
                        self.showingInv = not self.showingInv
                        self.updateDisplay = True
                    elif ch in self.movementKeys:
                        self.doAction('move', {'subject':self.entity, 'dx':self.movementKeys[ch][0], 'dy':self.movementKeys[ch][1]})
                    elif opcode == ord('r')-ord('a')+1:             # CTRL+R
                        self.updateDisplay = True
                    elif ch == 'S':
                        self.doQuit()
                    else:
                        logging.warning('unhandled key: {0} ({1})'.format(ch, opcode))
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
