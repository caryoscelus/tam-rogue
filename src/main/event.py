import worldregistry

class Event:
    def __init__(self, action, args, result):
        # TODO: move this to registry?
        if isinstance(action, str):
            action = worldregistry.world.actions[action]
        
        self.action = action
        self.args = args
        self.result = result
    
    def __str__(self):
        s = ''
        descriptor = self.action.attr('descriptor')
        if descriptor:
            raise NotImplementedError('descriptors are not supported yet')
        elif descriptor == None:
            logging.warning('action has no descriptor')
            s = 'action {0} happend on {1} with result: {2}'.format(self.action, self.args, self.result)
        else:
            logging.debug('descriptor set to do nothing')
        return s
