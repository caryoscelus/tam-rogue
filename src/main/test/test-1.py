#! /usr/bin/env python3

import sys
sys.path.append(".")
sys.path.append("..")

from client import *

if __name__ == '__main__':
    myClient = Client()
    myClient.connectClient(('localhost', 6985))
    myClient.redraw()
