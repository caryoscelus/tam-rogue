import random
import math

import logging
import xml.etree.ElementTree as ET

class MapVisualizer:
    # TODO: return full gfx, not only character
    def tileToGfx(self, tiledMap, x, y):
        upper = tiledMap.getTile(x, y).getUpper()
        if not upper:
            return ' '
        return upper.attr('char')
        #ground = tiledMap.getContent(x, y, 'ground')
        #objects = tiledMap.getContent(x, y, 'objects')
        #if objects:
            #obj = objects[-1]
            #entity = obj
        #else:
            #entity = ground
        
        #if not entity:
            #return ' '
        #entityType = entity.attr('class')
        #if entityType == 'floor':
            #return '.'
        #elif entityType == 'wall':
            #return '-'
        #elif entityType == 'human':
            #return '@'
        #else:
            #return '?'
    
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
                ET.SubElement(root, 'char', {'x':str(x), 'y':str(y), 'ch':ch})
        
        #f = 32
        #l = 128
        #ch = chr(math.floor(random.random()*(l-f)+f))
        
        #ET.SubElement(root, 'char', {'ch':ch, 'x':'12', 'y':'1'})
        
        return bytes(ET.tostring(root))
        #return bytes('<scrup>\n<char ch="'+ch+'" x="12" y="1"/>\n</scrup>', 'ascii')
