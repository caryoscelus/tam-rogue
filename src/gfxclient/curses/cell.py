class Cell:
    def __init__(self, char = ' ', color = 0, attr = 0):
        self.ch = char
        self.co = color
        self.a = attr
    
    def __str__(self):
        return self.ch
    
    def __repr__(self):
        return str(self)
