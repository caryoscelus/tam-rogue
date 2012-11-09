import logging

from entity import EntityDeadError

class EntityQueue:
    def __init__(self):
        self.content = []
        self.pos = 0
    
    #def pop(self):
        #result = None
        #while not result:
            #try:
                #entity = self.content.pop(0)
                #entity.check()
                #result = entity
            #except IndexError:
                #raise EmptyQueueError(self)
            #except EntityDeadError:
                #pass
        
        ## return to queue
        #self.push(entity)
        
        #return result
    
    def remove(self, entity):
        self.content.remove(entity)
    
    def pop(self):
        logging.debug('pop')
        
        result = None
        while not result:
            try:
                entity = self.content[self.pos]
                entity.check()
            except IndexError:
                raise EmptyQueueError(self)
            except EntityDeadError:
                del self.content[self.pos]
        self.pos += 1
        return result
    
    def reset(self):
        self.pos = 0
    
    def push(self, entity):
        entity.check()
        self.content.append(entity)


class EmptyQueueError(Exception):
    def __init__(self, queue):
        self.queue = queue
    
    #
