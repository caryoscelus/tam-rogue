import logging
import socket

class Receiver:
    def __init__(self, addr = None):
        self.connect(addr)
    
    def connect(self, addr):
        self.addr = addr
    
    def listen(self):
        logging.debug('listening..')
        return '<input opcode="33"/>'
