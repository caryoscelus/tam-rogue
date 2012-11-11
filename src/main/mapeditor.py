#! /usr/bin/env python3

import logging
import threading
import traceback

from displaying import Displaying

class MapEditor(Displaying):
    def __init__(self):
        self.quit = False
    
    def redraw(self):
        super().redraw()


def main(argv):
    if len(argv) < 2:
        raise RuntimeError('not enough command line arguments')
    
    me = MapEditor()
    me.start()

if __name__ == '__main__':
    logging.basicConfig(filename='mapeditor.log', level=logging.DEBUG)
    
    try:
        from sys import argv
        main(argv)
    except BaseException as err:
        logging.error(traceback.format_exc())
