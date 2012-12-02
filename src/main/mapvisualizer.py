import random
import math

import logging
import xml.etree.ElementTree as ET

class MapVisualizer:
    # TODO: return full gfx, not only character
    def tileToGfx(self, tiledMap, x, y):
        while True:
            upper = tiledMap.getTile(x, y).getUpper()
            if not upper:
                return ' '
            
            try:
                return upper.attr('char')
            except EntityAttributeError:
                logging.warning('unvisualizable entity')
                return '?'
            except BaseEntityDeadError:
                logging.debug('entity dead while trying to visualize')
    
    def toGfx(self, tiledMap):
        # TODO: remove stupid screen format
        screen = []
        screen.append({'height':tiledMap.height, 'width':tiledMap.width})
        screen.append(tiledMap.genMap(lambda x, y: self.tileToGfx(tiledMap, x, y)))
        return screen
    
    def toXml(self, tiledMap):
        screen = self.toGfx(tiledMap)
        
        root = ET.Element('scrup')
        
        for y in range(screen[0]['height']):
            for x in range(screen[0]['width']):
                ch = screen[1][y][x]
                # TODO: duck typing?..
                if isinstance(ch, str):
                    ET.SubElement(root, 'char', {'x':str(x), 'y':str(y), 'ch':ch})
                else:
                    logging.warning('unvisualizable display character')
        
        return root

from entity import EntityAttributeError
from baseentity import BaseEntityDeadError
