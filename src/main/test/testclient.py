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
    floor = Entity({'class':'floor'})
    wall = Entity({'class':'wall'})
    human = Entity({'class':'human', 'hp':2, 'hungry':0, 'maxHungry':10})
    human.order = ['weapon']
    human.content = {'weapon':None}
    dagger = Entity({'class':'dagger', 'hurt':2})
    human.put('weapon', dagger)
    fungus = Entity({'class':'fungus', 'hp':2})
    trap = Entity({'class':'trap', 'hurt':1})
    stairs = Entity({'class':'stairs', 'destination':2})
    human.alive = True
    
    map0 = TiledMap(20, 20, {'id':0})
    map0.alive = True
    map0.exist = True
    map0.queue.push(human)
    
    # TODO: use something else
    worldregistry.world.setMap(0, map0)
    
    # floor
    for y in range(1, 10):
        for x in range(2, 18):
            map0.getTile(x, y).put('ground', floor)
    
    # wall
    for x in range(2, 18):
        map0.getTile(x, 10).put('ground', wall)
    
    # objects
    map0.putOn(12, 4, 'monster', human)
    map0.putOn(15, 4, 'trap', trap)
    map0.putOn(15, 7, 'feature', stairs)
    map0.putOn(6, 6, 'monster', fungus)
    
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
