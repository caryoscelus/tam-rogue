import curses
import time
import logging
import traceback

from cell import Cell

class Display:
    def __init__(self):
        self.ready = False
        
        # common flags
        self.quit = False
        self.update = False
        
        self.alwaysUpdate = False
        self.wait = 1.0/64
        
        self.data = []
        self.width = 0
        self.height = 0
        
        self.cScr = None
        self.cPad = None
    
    def resize(self, w, h):
        self.width = w
        self.height = h
        self.filldata()
        self.cPad = curses.newpad(self.height, self.width+1)
    
    def filldata(self):
        self.data = [[Cell(' ') for x in range(self.width)] for y in range(self.height)]
    
    def init(self):
        # TODO: move to special curses-wrapping class
        # cause it affects input as well
        # TODO: use curses.wrapper
        self.cScr = curses.initscr()
        
        curses.noecho()
        curses.cbreak()
        self.cScr.keypad(1)
        self.cScr.nodelay(1)
        
        # TODO: remove constants
        self.resize(25, 80)
        
        self.ready = True
    
    def clean(self):
        self.cScr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    
    def loop(self):
        while not self.quit:
            try:
                if self.update or self.alwaysUpdate:
                    for y in range(self.height):
                        line = self.data[y]
                        for x in range(self.width):
                            try:
                                self.cPad.addstr(y, x, line[x].c)
                            except curses.error:
                                logging.debug('addstr failed ({0}, {1})'.format(x, y))
                    self.cPad.refresh(0, 0, 0, 0, self.width, self.height)
                    self.cScr.refresh()
                    
                    self.update = False
                if self.wait > 0:
                    time.sleep(self.wait)
            except Exception as err:
                logging.error('unhandled exception in display server:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
