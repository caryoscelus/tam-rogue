'''Central place for all kind of file (mods/saves/etc) loading'''

import xml.etree.ElementTree as ET
import logging

from mod import Mod

def modFromFile(modFile):
    try:
        f = open(modFile)
        modXml = f.read()
        f.close()
        
        newMod = Mod(ET.fromstring(modXml))
        
        return newMod
    except IOError:
        logging.warning('cannot load mod file {0}'.format(modFile))
    except ET.ParseError:
        logging.warning('cannot parse mod file {0}'.format(modFile))
    return None
