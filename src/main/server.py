import threading
import traceback
import logging

from serverclient import ServerClient

class Server:
    def __init__(self):
        self.clients = []
        self.thread = None
        self.world = None
        self.quit = False
        self.life = None
    
    def main(self):
        self.life = self.world.live()
        while not self.quit:
            try:
                next(self.life)
            except Exception as err:
                logging.error('unhandled exception in world server thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
    
    def start(self):
        self.thread = threading.Thread(None, self.main, 'world-server', ())
        self.thread.start()
    
    def stop(self):
        self.quit = True
    
    # called from client
    def connect(self, client):
        sc = ServerClient(client)
        self.clients.append(sc)
    
    def disconnect(self, sc):
        logging.info('client {0} disconnected'.format(sc))
        self.clients.remove(sc)
