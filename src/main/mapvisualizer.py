import random
import math

import logging
import xml.etree.ElementTree as ET

class MapVisualizer:
    # TODO: return full gfx, not only character
    def tileToGfx(self, tiledMap, x, y):
        upper = tiledMap.getTile(x, y).getUpper()
        if not upper:
            return ' ', None, None
        
        try:
            ch = upper.attr('char')
            try:
                co = upper.attr('color')
            except EntityAttributeError:
                co = None
            try:
                a = upper.attr('visual-effect')
            except EntityAttributeError:
                a = None
            return ch, co, a
        except EntityAttributeError:
            logging.warning('unvisualizable entity')
            return '?', 'red', 'reverse'
        except BaseEntityDeadError:
            logging.debug('entity dead while trying to visualize')
            return '?', 'red', 'reverse'
    
    def toGfx(self, tiledMap):
        # TODO: remove stupid screen format
        screen = []
        screen.append({'height':tiledMap.height, 'width':tiledMap.width})
        screen.append(tiledMap.genMap(lambda x, y: self.tileToGfx(tiledMap, x, y)))
        return screen
    
    def toXml(self, tiledMap, x0 = 0, y0 = 0):
        screen = self.toGfx(tiledMap)
        
        root = ET.Element('scrup')
        
        for y in range(screen[0]['height']):
            for x in range(screen[0]['width']):
                ch, co, a = screen[1][y][x]
                # TODO: duck typing?..
                if isinstance(ch, str):
                    attrs = {'x':str(x+x0), 'y':str(y+y0), 'ch':ch}
                    if co:
                        attrs['co'] = co
                    if a:
                        attrs['a'] = a
                    ET.SubElement(root, 'char', attrs)
                else:
                    logging.warning('unvisualizable display character')
        
        return root

from entity import EntityAttributeError
from baseentity import BaseEntityDeadError
