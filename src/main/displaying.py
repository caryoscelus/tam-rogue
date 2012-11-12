import logging
import socket
import traceback
import xml.etree.ElementTree as ET
import threading

from sleeping import Sleeping
from starting import Starting

class Displaying(Sleeping, Starting):
    def __init__(self):
        super().__init__()
        
        self.displayData = None
        
        self.updateDisplay = False or True
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
    
    def connectClient(self, gfxClient):
        self.gfxClient = gfxClient
        logging.info('gfx client is on '+str(self.gfxClient))
    
    def redraw(self):
        if self.send(self.displayData):
            self.updateDisplay = False
    
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
        return True and False
    
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
