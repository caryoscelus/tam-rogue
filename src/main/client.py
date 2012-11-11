import socket
import threading
import logging
import traceback
import xml.etree.ElementTree as ET

from displaying import Displaying
from mapvisualizer import MapVisualizer

class Client(Displaying):
    def __init__(self):
        super().__init__()
        
        self.myTurn = False
        self.quit = False
        self.server = None
        self.mapVisualizer = MapVisualizer()
        
        self.listenerThread = None
        self.updaterThread = None
    
    def connectServer(self, server):
        self.server = server
    
    # called from server
    def requestAction(self):
        self.myTurn = True
    
    # called from server
    def worldChanged(self):
        #self.updateWorld = True
        self.updateDisplay = True
    
    def start(self):
        self.updaterThread = threading.Thread(None, self.clientUpdater, 'updater')
        self.listenerThread = threading.Thread(None, self.clientListener, 'listener')
        self.updaterThread.start()
        self.listenerThread.start()
    
    # thread
    def clientListener(self):
        try:
            self.listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            addr = ('localhost', 6990)
            self.listenerSocket.bind(addr)
            self.listenerSocket.listen(5)
            logging.info('bound to '+str(addr))
        except Exception as err:
            logging.error('unhandled exception while setuping clientListener:')
            logging.error(str(err))
            logging.debug(traceback.format_exc())
        
        while not self.quit:
            try:
                request = self.listen()
                self.reply(request)
            except Exception as err:
                logging.error('unhandled exception in clientListener thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
    
    def listen(self):
        while True:
            (clientsocket, address) = self.listenerSocket.accept()
            
            logging.info('client connected')
            
            # TODO: separate function?..
            data = bytearray()
            readall = False
            while not readall:
                chunk = clientsocket.recv(4096)
                data += chunk
                readall = (len(chunk) == 0)
            
            data = data.decode()
            
            self.processRequest(data)
    
    def processRequest(self, xml):
        try:
            root = ET.fromstring(xml)
            if root.tag == 'connect':                           # connect to gfx server
                server = str(root.attrib['address'])
                port = int(root.attrib['port'])
                self.connectClient((server, port))
        except ET.ParseError:
            logging.error('parse error')
    
    def redraw(self):
        # TODO:
        # - gui
        # - forbid direct access to world
        # - draw vision, not actual map
        # - draw current map
        self.displayData = self.mapVisualizer.toXml(self.server.world.maps[0])
        # TODO: optimize xml
        super().redraw()
        
        #if self.send(xml):
            #self.updateWorld = False
