def Direct(x, y):
    '''Pack x, y direction to one integer'''
    if (not x in range(-1, 2)) or (not y in range(-1, 2)):
        raise ValueError('direction ({0}, {1}) not in range'.format(x, y))
    return (x+1)*3+(y+1)

def UnDirect(d):
    '''Convert integer packed direction to x, y'''
    if not d in range(9):
        raise ValueError('direction {0} not in range'.format(d))
    return d//3-1, d%3-1
