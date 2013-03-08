def Direct(x, y):
    '''Pack x, y direction to one integer'''
    return (x+1)*3+(y+1)

def UnDirect(d):
    '''Convert integer packed direction to x, y'''
    return d//3-1, d%3-1
