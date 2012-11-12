import socket
import logging
import traceback
import xml.etree.ElementTree as ET

from display import Display
from cell import Cell

class DisplayServer:
    display = None
    
    quit = False
    
    def __init__(self, disp = None):
        self.display = disp
    
    def init(self, myAddr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(myAddr)
        self.socket.listen(5)
    
    def loop(self):
        while not self.quit:
            try:
                (clientsocket, address) = self.socket.accept()
                
                # read data
                data = bytearray()
                readall = False
                while not readall:
                    chunk = clientsocket.recv(4096)
                    data += chunk
                    readall = (len(chunk) == 0)
                
                data = data.decode()
                
                # process data
                # TODO: add different protocol support
                try:
                    root = ET.fromstring(data)
                    if root.tag == 'scrup':
                        for cell in root:
                            x = int(cell.attrib['x'])
                            y = int(cell.attrib['y'])
                            ch = cell.attrib['ch']
                            self.display.data[y][x].c = ch
                    self.display.update = True
                except ET.ParseError:
                    logging.error('parse error')
            except Exception as err:
                logging.error('unhandled exception in display server thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
            
    
    def clean(self):
        pass
