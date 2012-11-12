#! /usr/bin/env python3

import logging
import threading
import traceback

from displaying import Displaying
from inputting import Inputting
from tiledmap import TiledMap
from mapvisualizer import MapVisualizer
from worldregistry import sysWorldRegistry

class MapEditor(Displaying, Inputting):
    def __init__(self):
        super().__init__()
        self.quit = False
        self.tiledMap = None
        self.mapVisualizer = MapVisualizer()
    
    def start(self):
        super().start()
    
    def redraw(self):
        # draw map
        self.displayData = self.mapVisualizer.toXml(self.tiledMap)
        super().redraw()
    
    def loadMapXml(self, mapXml):
        self.tiledMap = TiledMap.fromXml(mapXml)


def main(argv):
    import xml.etree.ElementTree as ET
    
    if len(argv) < 2:
        raise RuntimeError('not enough command line arguments')
    
    sysWorldRegistry.loadMod('test/character-mod.xml')
    
    try:
        fname = argv[1]
        f = open(fname)
        mapXml = ET.fromstring(f.read())
        f.close()
    except IOError:
        logging.error(traceback.format_exc())
        raise RuntimeError('error while reading file')
    
    me = MapEditor()
    # TODO: remove constants
    addr = ('localhost', 6991)
    me.connect(addr)
    me.loadMapXml(mapXml)
    me.start()

if __name__ == '__main__':
    logging.basicConfig(filename='mapeditor.log', level=logging.DEBUG)
    
    try:
        from sys import argv
        main(argv)
    except BaseException as err:
        logging.error(traceback.format_exc())
