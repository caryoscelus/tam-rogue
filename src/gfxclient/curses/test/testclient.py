#! /usr/bin/env python3

import sys
sys.path.append(".")
sys.path.append("..")

from cell import Cell

import math
import time
import random
import socket
import xml.etree.ElementTree as ET

width = 80
height = 25

screen = [[Cell('.') for x in range(width)] for y in range(height)]

def screenToXml(scr):
    root = ET.Element('scrup')
    
    for y in range(height):
        for x in range(width):
            ch = screen[y][x].c
            ET.SubElement(root, 'char', {'x':str(x), 'y':str(y), 'ch':ch})
    
    return ET.tostring(root)

def send():
    message = screenToXml(screen)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 6985))
    
    sock.sendall(message)
    
    #sock.shutdown(1)
    sock.close()

def modify():
    y = math.floor(random.random()*height)
    x = math.floor(random.random()*width)
    y, x = 6, 20
    c = chr(math.floor(random.random()*(128-32)+32))
    
    screen[y][x] = Cell(c)

def sleep():
    time.sleep(0.001)

def main():
    while True:
        send()
        modify()
        sleep()

if __name__ == '__main__':
    main()
