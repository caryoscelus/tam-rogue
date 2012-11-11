#! /usr/bin/env python3

import logging
import threading
import traceback

from displaying import Displaying
from tiledmap import TiledMap
from mapvisualizer import MapVisualizer

class MapEditor(Displaying):
    def __init__(self):
        super().__init__()
        self.quit = False
        self.tiledMap = None
        self.mapVisualizer = MapVisualizer()
    
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
    
    try:
        fname = argv[1]
        f = open(fname)
        mapXml = ET.fromstring(f.read())
        f.close()
    except IOError:
        logging.error(traceback.format_exc())
        raise RuntimeError('error while reading file')
    
    me = MapEditor()
    me.loadMapXml(mapXml)
    me.start()

if __name__ == '__main__':
    logging.basicConfig(filename='mapeditor.log', level=logging.DEBUG)
    
    try:
        from sys import argv
        main(argv)
    except BaseException as err:
        logging.error(traceback.format_exc())
