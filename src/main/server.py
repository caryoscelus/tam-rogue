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
    
    # called from client
    def connect(self, client):
        sc = ServerClient(self, client)
        self.clients.append(sc)
        
        # NOTE: this will always fail anyway
        #try:
            #sc.register()
        #except Exception as err:
            #logging.warning('error while registering client')
            #logging.debug(traceback.format_exc())
        
        return sc
    
    def disconnect(self, sc):
        logging.info('client {0} disconnected'.format(sc))
        self.clients.remove(sc)
