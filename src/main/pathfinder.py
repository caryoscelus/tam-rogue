from tiledmap import TiledMap

DIRECTS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

class PathFinder:
    def __init__(self, tmap):
        self.tmap = tmap
    
    # implement this function
    def getPrice():
        return False
    
    # TODO: implement
    def pathFind(self, x0, y0, x1, y1):
        # algorythm: create cost map
        # TODO: optimize
        costMap = self.tmap.genMap(lambda x, y: None)
        x = x0
        y = y0
        direct = 0
        while True:
            pass
