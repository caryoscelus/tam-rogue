#! /usr/bin/env python3

import logging
import threading

from sleeping import Sleeping

class MapEditor(Sleeping):
    def __init__(self):
        self.quit = False
    
    def start(self):
        self.updaterThread = threading.Thread(None, self.clientUpdater, 'updater')
        self.updaterThread.start()
    
    # thread
    def clientUpdater(self):
        while not self.quit:
            try:
                if self.updateWorld:
                    self.redraw()
                self.sleep()
            except Exception as err:
                logging.error('unhandled exception in clientUpdater thread:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())


if __name__ == '__main__':
    from sys import argv
    
    if len(argv) < 2:
        raise RuntimeError('not enough command line arguments')
    
    logging.basicConfig(filename='mapeditor.log', level=logging.DEBUG)
    
    me = MapEditor()
    me.start()
