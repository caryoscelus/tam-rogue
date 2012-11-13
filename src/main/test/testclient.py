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

def testClient():
    logging.basicConfig(filename='testclient.log', level=logging.DEBUG)
    myClient = Client()
    myClient.connectClient(('localhost', 6985))
    myClient.start()

def generateWorld():
    floor = Entity({'class':'floor'})
    wall = Entity({'class':'wall'})
    human = Entity({'class':'human', 'hp':20})
    human.alive = True
    
    map0 = TiledMap(20, 20, {'ground':None, 'objects':[]}, ['ground', 'objects'])
    map0.alive = True
    map0.queue.push(human)
    # floor
    for y in range(1, 10):
        for x in range(2, 18):
            map0.getTile(x, y).put('ground', floor)
    
    # wall
    for x in range(2, 18):
        map0.getTile(x, 10).put('ground', wall)
    
    # human
    map0.getTile(12, 4).put('objects', human)
    
    sysWorldRegistry.world.maps.append(map0)
    
    return human

def testClientServer(server, port):
    myServer = Server()
    
    sysWorldRegistry.loadMod('character-mod.xml')
    human = generateWorld()
    
    myServer.start()
    myClient = Client()
    myClient.entity = human
    myClient.connectClient((server, port)) #'localhost', 6985))
    myClient.connectServer(myServer)
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
