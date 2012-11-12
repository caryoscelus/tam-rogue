import logging
import xml.etree.ElementTree as ET

class InputReader:
    def __init__(self, disp, backSender):
        self.disp = disp
        self.backSender = backSender
    
    def loop(self):
        while not self.disp.quit:
            try:
                opcode = self.disp.cScr.getch()
                self.processKey(opcode)
            except Exception as err:
                logging.error('unhandled exception in input reader')
                logging.debug(err)
    
    def processKey(self, opcode):
        root = ET.Element('input', {'opcode':str(opcode)})
        self.backSender.send(ET.tostring(root))
