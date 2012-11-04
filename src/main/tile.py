import copy

from entity import EntityDeadError
import server

class Tile:
    # order - list: int -> string
    # content - dict: string -> Entity/list
    # if list, it's extandable position
    def __init__(self, content, order):
        self.order = order
        self.content = copy.deepcopy(content)
    
    def get(self, position):
        try:
            self.content[position].check()
            return self.content[position]
        except AttributeError:                          # raised on lists
            return self.content[position]
        except EntityDeadError:                         # raised on destroyed object
            self.content[position] = None
            return None
        except KeyError:                                # raised on no position
            extPositions = server.globalServer.world.tileLayers
            try:
                t = copy.deepcopy(extPositions[position])
                self.content[position] = t
                return t
            except KeyError:
                raise TilePositionError(position)
    
    def getUpper(self):
        # no need for modding cause objects cannot be placed in mod positions
        for position in reversed(self.order):
            try:
                e = self.get(position)
                e.check()
                return e
            except AttributeError:                      # on lists
                try:
                    return e[-1]
                except IndexError:                      # on empty lists
                    pass
                except TypeError:                       # on None
                    pass
        return None
    
    def put(self, position, entity):
        # check if position is ok
        self.get(position)
        
        try:
            self.content[position].append(entity)
        except KeyError:
            logging.error('this could not happen!')
            raise TilePositionError(position)
        except AttributeError:                          # non-list
            try:
                self.content[position].check()
                raise TileTakenError(position)
            except AttributeError:                      # raised on non-entity objects (only None is allowed)
                self.content[position] = entity
            except EntityDeadError:                     # raised on destroyed
                self.content[position] = entity
    
    # is it useful?..
    def isValid(self, position):
        try:
            self.get(position)
            return True
        except TilePositionError:
            return False

class TileTakenError(Exception):
    def __init__(self, key):
        self.key = key
    
    def __str__(self):
        # TODO: fancy output
        return repr(self.key)

class TilePositionError(Exception):
    def __init__(self, key):
        self.key = key
