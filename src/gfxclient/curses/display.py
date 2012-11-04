import curses
import time
import logging
import traceback

from cell import Cell

class Display:
    ready = False
    
    # common flags
    quit = False
    update = False
    
    alwaysUpdate = False
    wait = 1.0/32
    
    data = []
    width = 0
    height = 0
    
    cScr = None
    cPad = None
    
    def __init__(self):
        pass
    
    def filldata(self):
        self.data = [[Cell('a') for x in range(self.width)] for y in range(self.height)]
    
    def init(self):
        # TODO: move to special curses-wrapping class
        # cause it affects input as well
        # TODO: use curses.wrapper
        self.cScr = curses.initscr()
        
        curses.noecho()
        curses.cbreak()
        self.cScr.keypad(1)
        
        #self.height, self.width = self.cScr.getmaxyx()
        self.height, self.width = 25, 80
        
        self.filldata()
        self.cPad = curses.newpad(self.height, self.width+1)
        
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
                            self.cPad.addstr(y, x, line[x].c) #, line[x].a)
                            #self.cPad.addch(4, 18, ord('c'))
                    self.cPad.refresh(0, 0, 0, 0, 12, 80)
                    self.cScr.refresh()
                    
                    self.update = False
                if self.wait > 0:
                    time.sleep(self.wait)
            #except KeyboardInterrupt:
                #self.quit = True
            except Exception as err:
                logging.error('unhandled exception in display server:')
                logging.error(str(err))
                logging.debug(traceback.format_exc())
