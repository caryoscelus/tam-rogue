'''Central place for all kind of file (mods/saves/etc) loading'''

import xml.etree.ElementTree as ET
import logging
import os.path

from mod import Mod

_modPath = ['']

def modFromFile(modFile):
    '''Load mod from file (respecting _modPath)'''
    
    f = None
    modXml = None
    for path in _modPath:
        try:
            f = open(os.path.join(path, modFile))
            modXml = f.read()
            f.close()
            break
        except IOError:
            pass
    if f:
        try:
            newMod = Mod(ET.fromstring(modXml))
        except ET.ParseError:
            logging.warning('cannot parse mod file {0}'.format(modFile))
            return None
        
        return newMod
    else:
        logging.warning('cannot load mod file {0}'.format(modFile))
    return None

def addPath(path):
    '''Add mod search path'''
    _modPath.append(path)
