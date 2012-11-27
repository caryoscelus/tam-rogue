import logging
import socket
import traceback
import xml.etree.ElementTree as ET
import threading

from sleeping import Sleeping
from starting import Starting
from receiver import Receiver

class Displaying(Sleeping, Starting, Receiver):
    def __init__(self):
        super().__init__()
        
        self.displayData = ET.Element('scrup')
        
        self.updateDisplay = True
        self.gfxClient = None
        self.updaterThread = threading.Thread(None, self.clientUpdater, 'updater')
        self.listenerThread = threading.Thread(None, self.clientListener, 'listener')
    
    def start(self):
        super().start()
        self.updaterThread.start()
        self.listenerThread.start()
    
    # thread
    def clientUpdater(self):
        while not self.quit:
            try:
                if self.updateDisplay:
                    self.redraw()
                self.sleep()
            except Exception as err:
                logging.error('unhandled exception in clientUpdater thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
        logging.info('clientUpdater() finished')
    
    def connectClient(self, gfxClient):
        self.gfxClient = gfxClient
        logging.info('gfx client is on '+str(self.gfxClient))
    
    # TODO: support styles/effects
    def putChar(self, x, y, ch):
        # TODO: override instead of appending!
        ET.SubElement(self.displayData, 'char', {'x':str(x), 'y':str(y), 'ch':ch})
        self.updateDisplay = True
    
    def putString(self, x, y, s):
        # TODO: length control
        for ch in s:
            self.putChar(x, y, ch)
            x += 1
    
    def resize(self, width, height):
        logging.debug('resize')
        self.send(bytes('<resize width="{0}" height="{1}"/>'.format(width, height), 'ascii'))
    
    def redraw(self):
        # TODO: optimize xml
        msg = bytes(ET.tostring(self.displayData))
        if self.send(msg):
            self.updateDisplay = False
    
    # TODO: separate?
    def send(self, data):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.gfxClient)
            
            sock.sendall(data)
            
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except socket.error as err:
            logging.warning('net error')
            logging.debug(err)
            return False
        except Exception as err:
            logging.warning('unknown error while connecting')
            logging.debug(err)
            return False
        return True
    
    def notifyDisconnection(self):
        '''Notify gfx client about disconnection'''
        # TODO: use proper generation?
        if self.send(bytes('<?xml version="1.0" encoding="UTF-8"?><close/>\n', 'ascii')):
            logging.info('gfx client was successfully notified about disconnection')
        else:
            logging.warning('gfx client wasn\'t notified, exiting anyway')
    
    # thread
    # TODO: one listener per app
    def clientListener(self):
        self.allowListening()
        
        while not self.quit:
            try:
                request = self.listen()
                # if connected: one connection per server is ok by now
                if self.processRequest(request):
                    break
            except Exception as err:
                logging.error('unhandled exception in clientListener thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
    
    def processRequest(self, xml):
        try:
            root = ET.fromstring(xml)
            if root.tag == 'connect':                           # connect to gfx server
                server = str(root.attrib['address'])
                port = int(root.attrib['port'])
                self.connectClient((server, port))
                return True
        except ET.ParseError:
            logging.error('parse error')
