def Direct(x, y):
    '''Pack x, y direction to one integer'''
    if not x in (-1, 2) or not y in (-1, 2):
        raise ValueError('direction x, y not in range')
    return (x+1)*3+(y+1)

def UnDirect(d):
    '''Convert integer packed direction to x, y'''
    if not d in range(9):
        raise ValueError('direction not in range')
    return d//3-1, d%3-1
