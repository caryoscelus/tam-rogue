#! /usr/bin/env python3

import logging
import threading
import traceback
import xml.etree.ElementTree as ET

from displaying import Displaying
from inputting import Inputting
from tiledmap import TiledMap
from mapvisualizer import MapVisualizer
from worldregistry import sysWorldRegistry
from entity import Entity

class MapEditor(Displaying, Inputting):
    def __init__(self):
        super().__init__()
        self.quit = False
        self.mapVisualizer = MapVisualizer()
        
        self.tiledMap = None
        
        self.cursor = [0, 0]
    
    def start(self):
        super().start()
    
    def redraw(self):
        # draw map
        self.displayData = self.mapVisualizer.toXml(self.tiledMap)
        super().redraw()
    
    def loadMapXml(self, mapXml):
        self.tiledMap = TiledMap.fromXml(mapXml)
    
    def saveMapXml(self):
        return self.tiledMap.saveXml()
    
    def processKey(self, opcode):
        logging.debug('key pressed: {0}'.format(chr(opcode)))
        
        try:
            ch = chr(opcode)
            if ch == 'h':
                self.cursor[0] -= 1
            elif ch == 'j':
                self.cursor[1] += 1
            elif ch == 'k':
                self.cursor[1] -= 1
            elif ch == 'l':
                self.cursor[0] += 1
            elif ch == '.':
                floor = Entity({'class':'floor'})
                self.tiledMap.putOn(self.cursor[0], self.cursor[1], 'ground', floor)
            elif ch == 'D':
                logging.debug(ET.tostring(self.saveMapXml()))
        except Exception as err:
            logging.error('unhandled exception while processing key')
            logging.error(err)
            logging.debug(traceback.format_exc())


def main(argv):
    if len(argv) < 2:
        raise RuntimeError('not enough command line arguments')
    
    sysWorldRegistry.loadMod('test/character-mod.xml')
    
    # TODO: put reading file into MapEditor
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
    addr = ('localhost', 6990)
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
