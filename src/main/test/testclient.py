#! /usr/bin/env python3

import logging
import traceback

import sys
sys.path.append(".")
sys.path.append("..")

from client import *
from server import *
from world import *
from tiledmap import *
from tile import *
from entity import *
from worldregistry import *

# TODO: remove from here; make proper loading/generation
def generateWorld():
    human = Entity({'class':'human', 'hp':2, 'hungry':0, 'maxHungry':5})
    human.order = ['weapon']
    human.content = {'weapon':None}
    dagger = Entity({'class':'dagger', 'hurt':2})
    human.put('weapon', dagger)
    human.alive = True
    
    map0 = worldregistry.world.getMap(0)
    map0.notifyEmpty()
    
    map0.alive = True
    map0.queue.push(human)
    upstairs = map0.attr('stairs-down')
    map0.putOn(upstairs[0], upstairs[1], 'monster', human)
    
    return human

# TODO: remove constants
def testClientServer(server, port):
    myServer = Server()
    
    worldregistry.loadMod('basic-modpack.xml')
    human = generateWorld()
    
    myServer.start()
    myClient = Client()
    myClient.connectClient((server, port)) #'localhost', 6985))
    myClient.connectServer(myServer)
    myClient.loadMod('keymap.xml')
    
    # TODO: move to server
    myClient.askForEntity(human)
    
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
            port = 6985+2
        else:
            server = argv[1]
            port = int(argv[2])
        testClientServer(server, port)
    except BaseException as err:
        logging.error(traceback.format_exc())
