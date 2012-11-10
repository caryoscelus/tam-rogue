#! /usr/bin/env python3

import logging

import sys
sys.path.append(".")
sys.path.append("..")

from client import *
from server import *
from world import *
from tiledmap import *
from tile import *
from entity import *

def testClient():
    logging.basicConfig(filename='testclient.log', level=logging.DEBUG)
    myClient = Client()
    myClient.connectClient(('localhost', 6985))
    myClient.start()

def generateWorld():
    floor = Entity({'class':'floor'})
    wall = Entity({'class':'wall'})
    human = Entity({'class':'human'})
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
    
    world = World()
    world.maps.append(map0)
    return world

def testClientServer(server, port):
    logging.basicConfig(filename='testclient.log', level=logging.DEBUG)
    myServer = Server()
    myServer.world = generateWorld()
    myServer.loadMod('character-mod.xml')
    myServer.start()
    myClient = Client()
    myClient.connectClient((server, port)) #'localhost', 6985))
    myClient.connectServer(myServer)
    myClient.start()
    logging.info('client started')

if __name__ == '__main__':
    from sys import argv
    if len(argv) < 3:
        server = 'localhost'
        port = 6985+2
    else:
        server = argv[1]
        port = int(argv[2])
    testClientServer(server, port)