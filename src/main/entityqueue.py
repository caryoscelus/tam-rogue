import logging

from baseentity import BaseEntityDeadError

class EntityQueue:
    def __init__(self):
        self.content = []
        self.pos = 0
    
    def remove(self, anEntity):
        try:
            self.content.remove(anEntity)
        except ValueError:
            logging.warning('trying to remove non-pressent Entity from EntityQueue')
            logging.debug('Entity was: {0}'.format(anEntity))
    
    def pop(self):
        anEntity = None
        while not anEntity:
            try:
                anEntity = self.content[self.pos]
                anEntity.check()
                break
            except IndexError:
                raise EmptyQueueError(self)
            except BaseEntityDeadError:
                del self.content[self.pos]
        self.pos += 1
        return anEntity
    
    def reset(self):
        self.pos = 0
    
    def push(self, anEntity):
        anEntity.check()
        self.content.append(anEntity)


class EmptyQueueError(Exception):
    def __init__(self, queue):
        self.queue = queue
