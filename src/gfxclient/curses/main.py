#! /usr/bin/env python3

import threading
import logging
import time
import socket

from displayserver import DisplayServer
from display import Display
from cell import Cell
from inputreader import InputReader

def main(myAddr, clAddr):
    myDisplay = Display()
    myDisplay.init()
    
    # start threads
    displayThread = threading.Thread(None, displayMain, 'display', (myDisplay, ))
    displayThread.start()
    
    serverThread = threading.Thread(None, displayServerMain, 'displayserver', (myDisplay, myAddr))
    serverThread.start()
    
    connectTread = threading.Thread(None, connectMain, 'connection', (myAddr, clAddr))
    connectTread.start()
    
    inputThread = threading.Thread(None, inputMain, 'input', (myDisplay, ))
    inputThread.start()
    
    # wait till threads end
    while displayThread.is_alive() and serverThread.is_alive():
        try:
            littlePause = 0.1
            displayThread.join(littlePause)
        except KeyboardInterrupt:
            logging.info('exit on keyboard interrupt')
            myDisplay.quit = True
        except Exception as err:
            logging.error('unhandled exception in main thread:')
            logging.error(str(err))
            logging.debug(traceback.format_exc())

def tryConnect(myAddr, clAddr):
    # TODO: replace with xml generating
    message = bytes('<connect address="'+myAddr[0]+'" port="'+str(myAddr[1])+'" />', 'ascii')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(clAddr)
    
    sock.sendall(message)
    
    sock.close()
    
    return True

def connectMain(myAddr, clAddr):
    if not clAddr:
        return
    pause = 1
    connected = False
    while not connected:
        time.sleep(pause)
        try:
            connected = tryConnect(myAddr, clAddr)
        except socket.error:
            logging.error('error connecting to '+str(clAddr))
        pause *= 2
    
    logging.info('connection thread exit')

def displayServerMain(disp, myAddr):
    myServer = DisplayServer(disp)
    myServer.init(myAddr)
    myServer.loop()
    myServer.clean()

def displayMain(disp):
    disp.loop()
    disp.clean()

def inputMain(disp):
    inputReader = InputReader(disp)
    inputReader.loop()

if __name__ == '__main__':
    logging.basicConfig(filename='ascii-curses.log', level=logging.DEBUG)
    
    myServer = 'localhost'
    myPort = 6985
    
    clServer = 'localhost'
    clPort = 6990
    
    from sys import argv
    if len(argv) >= 3:
        myServer = str(argv[1])
        myPort = int(argv[2])
    if len(argv) >= 5:
        clServer = str(argv[3])
        clPort = int(argv[4])
    main((myServer, myPort), (clServer, clPort))
