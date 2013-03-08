import curses
import time
import logging
import traceback

from cell import Cell
from colors import COLORS

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
    
    def initColors(self):
        curses.start_color()
        n = 0
        for color in COLORS:
            c = color[1]
            if c:
                curses.init_pair(n, c, curses.COLOR_BLACK)
            n += 1
    
    def init(self):
        # TODO: move to special curses-wrapping class
        # cause it affects input as well
        # TODO: use curses.wrapper
        self.cScr = curses.initscr()
        
        curses.noecho()
        curses.cbreak()
        self.cScr.keypad(1)
        self.cScr.nodelay(1)
        
        self.initColors()
        
        # TODO: remove constants
        self.resize(80, 25)
        
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
                    logging.debug("update {0} {1}".format(self.width, self.height))
                    for y in range(self.height):
                        line = self.data[y]
                        logging.debug(''.join([str(e) for e in line]))
                        for x in range(self.width):
                            try:
                                a = curses.color_pair(line[x].co) ^ line[x].a
                                self.cPad.addstr(y, x, line[x].ch, a)
                            except curses.error:
                                logging.debug('addstr failed ({0}, {1})'.format(x, y))
                    self.cPad.refresh(0, 0, 0, 0, self.height, self.width)
                    self.cScr.refresh()
                    
                    self.update = False
                if self.wait > 0:
                    time.sleep(self.wait)
            except Exception as err:
                logging.error('unhandled exception in display server:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
