import threading
import traceback
import logging

from serverclient import ServerClient
import worldregistry

class Server:
    def __init__(self):
        self.clients = []
        self.thread = None
        self.quit = False
        self.life = None
    
    def main(self):
        while not self.quit:
            try:
                worldregistry.world.step()
            except Exception as err:
                logging.error('unhandled exception in world server thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
        logging.info('server main() quit')
    
    def start(self):
        self.thread = threading.Thread(None, self.main, 'world-server', ())
        self.thread.start()
    
    def stop(self):
        self.quit = True
    
    def connect(self, client):
        '''Client wants to connect to self'''
        sc = ServerClient(self, client)
        self.clients.append(sc)
        return sc
    
    def disconnect(self, sc):
        logging.info('client {0} disconnected'.format(sc))
        self.clients.remove(sc)
