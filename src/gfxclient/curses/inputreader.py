import logging
import xml.etree.ElementTree as ET

class InputReader:
    def __init__(self, disp, backSender):
        self.disp = disp
    
    def loop(self):
        while not self.disp.quit:
            try:
                opcode = self.disp.cScr.getch()
                self.processKey(opcode)
            except:
                logging.error('unhandled exception in input reader')
    
    def processKey(self, opcode):
        root = ET.Element('input', {'opcode':opcode})
        self.backSender.send(root.toString())
