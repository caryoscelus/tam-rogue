from colors import NAMED_COLORS

class Cell:
    def __init__(self, char = ' ', color = 0, attr = 0):
        self.ch = char
        self.co = self.convert(color)
        self.a = self.convert(attr)
    
    def convert(self, s):
        if isinstance(s, str):
            c = NAMED_COLORS[s]
            return c
        elif not s:
            return 0
        return s
    
    def __str__(self):
        return self.ch
    
    def __repr__(self):
        return str(self)
