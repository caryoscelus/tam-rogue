import logging

from entity import EntityDeadError

class EntityQueue:
    def __init__(self):
        self.content = []
        self.pos = 0
    
    def remove(self, entity):
        try:
            self.content.remove(entity)
        except ValueError:
            logging.warning('trying to remove non-pressent Entity from EntityQueue')
            logging.debug('Entity was: {0}'.format(entity))
    
    def pop(self):
        entity = None
        while not entity:
            try:
                entity = self.content[self.pos]
                entity.check()
                break
            except IndexError:
                raise EmptyQueueError(self)
            except EntityDeadError:
                del self.content[self.pos]
        self.pos += 1
        return entity
    
    def reset(self):
        self.pos = 0
    
    def push(self, entity):
        entity.check()
        self.content.append(entity)


class EmptyQueueError(Exception):
    def __init__(self, queue):
        self.queue = queue
