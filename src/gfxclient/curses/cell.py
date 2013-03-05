class Cell:
    def __init__(self, char = ' ', color = 0):
        self.c = char
        self.a = color
    
    def __str__(self):
        return self.c
    
    def __repr__(self):
        return str(self)
