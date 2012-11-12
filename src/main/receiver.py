import logging
import socket

class Receiver:
    def __init__(self, addr = None):
        self.listenerSocket = None
        self.connect(addr)
    
    def connect(self, addr):
        if addr:
            self.addr = addr
            self.listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            self.listenerSocket.bind(addr)
            self.listenerSocket.listen(5)
    
    def listen(self):
        (clientsocket, address) = self.listenerSocket.accept()
        
        logging.info('somebody connected to Receiver')
        
        # TODO: separate function?..
        data = bytearray()
        readall = False
        while not readall:
            chunk = clientsocket.recv(4096)
            data += chunk
            readall = (len(chunk) == 0)
        
        data = data.decode()
        return data
