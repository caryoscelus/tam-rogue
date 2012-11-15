import logging
import xml.etree.ElementTree as ET

from worldregistry import sysWorldRegistry

# TODO: raise errors instead of logging?..
def loadPack(xmlFile):
    try:
        f = open(xmlFile)
        t = f.read()
        f.close()
        
        root = ET.fromstring(t)
        
        if root.tag == 'modpack':
            for node in root:
                if node.tag == 'load':
                    try:
                        fname = node.attrib['file']
                        sysWorldRegistry.loadMod(fname)
                    except KeyError:
                        logging.error('no file property')
                else:
                    logging.warning('unknown node in modpack file {0}'.format(xmlFile))
        else:
            logging.warning('unknown kind of modpack ({0})'.format(xmlFile))
    except IOError:
        logging.error('error reading modpack file {0}'.format(xmlFile))
    except ET.ParseError:
        logging.error('error parsing modpack file {0}'.format(xmlFile))
