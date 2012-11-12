import socket

class BackSender:
    def __init__(self, addr):
        self.addr = addr
    
    def send(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.addr)
        
        sock.sendall(message)
        
        sock.close()
