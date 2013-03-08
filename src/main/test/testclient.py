#! /usr/bin/env python3

import logging
import traceback

import sys
sys.path.append(".")
sys.path.append("..")

from client import *
from botclient import *
from server import *
from world import *
from tiledmap import *
from tile import *
from entity import *
from worldregistry import *

# TODO: remove constants
def testClientServer(server, port):
    myServer = Server()
    
    worldregistry.loadMod('config.xml')
    player = worldregistry.world.actions['startup'].applyAction({})
    
    myServer.start()
    myClient = Client()
    myClient.connectClient((server, port))
    myClient.connectServer(myServer)
    myClient.loadMod('keymap.xml')
    myClient.loadMod('display-attr.xml')
    
    # TODO: move to server
    myClient.askForEntity(player)
    
    addr = ('localhost', 6990)
    myClient.connect(addr)
    myClient.start()
    logging.info('client started')

if __name__ == '__main__':
    logging.basicConfig(filename='testclient.log', level=logging.DEBUG)
    try:
        from sys import argv
        if len(argv) < 3:
            server = 'localhost'
            port = 6985
        else:
            server = argv[1]
            port = int(argv[2])
        testClientServer(server, port)
    except BaseException as err:
        logging.error(traceback.format_exc())
