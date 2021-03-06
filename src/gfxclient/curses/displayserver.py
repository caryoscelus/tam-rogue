import socket
import logging
import traceback
import xml.etree.ElementTree as ET

from display import Display
from cell import Cell

class DisplayServer:
    def __init__(self, disp = None):
        self.display = disp
        self.quit = False
    
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
                            co = cell.get('co')
                            a = cell.get('a')
                            try:
                                self.display.data[y][x] = Cell(ch, co, a)
                            except IndexError:
                                logging.warning('out of screen')
                        self.display.update = True
                    elif root.tag == 'close':
                        logging.info('connection closed, quitting')
                        self.quit = True
                        self.display.quit = True
                    elif root.tag == 'resize':
                        width = int(root.attrib['width'])
                        height = int(root.attrib['height'])
                        logging.debug('resize to {0}x{1}'.format(width, height))
                        self.display.resize(width, height)
                    else:
                        logging.warning('unknown tag "{0}"'.format(root.tag))
                except ET.ParseError:
                    logging.error('parse error')
                    logging.debug(traceback.format_exc())
                    logging.debug('received data: '.format(data))
            except Exception as err:
                logging.error('unhandled exception in display server thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
            
    
    def clean(self):
        pass
