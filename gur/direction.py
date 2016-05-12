def oppositeDir(d):
    if d == 'W':
        return 'E'
    elif d == 'N':
        return 'S'
    elif d == 'E':
        return 'W'
    elif d == 'S':
        return 'N'
    else:
        raise Error('Unknown dir')

dirPlus1 = {'N':'E', 'E':'S', 'S':'W', 'W':'N'}
dirMinus1 = {'N':'W', 'E':'N', 'S':'E', 'W':'S'}

diriter = {'N','E','S','W'}

def getMovementTime(d,w):
    if (d == 'N' or d == 'S') and w != 'r':
        # movement is slow and length is long
        return 5
    elif (d == 'E' or d == 'W') and w == 'r':
        # movement fast and lenght short
        return 2
    else:
        # movement fast and long or movement slow and short
        return 3

def edg(node, d):
    assert d in diriter, "%r" % d
    x,y = node
    if d == 'W': # west
        return (x - 1, y)
    elif d == 'N': # north
        return (x, y - 1)
    elif d == 'E':
        return (x+1, y)
    elif d == 'S':
        return (x, y + 1)

def neighbours(node):
    x,y = node
    yield (x-1,y)
    yield (x,y-1)
    yield (x+1,y)
    yield (x,y+1)


def getEdgeDir(e):
    u,v = e
    for d in diriter:
        if edg(u,d) == v:
            return d
    assert False, 'Edge %r is not a valid grid edge' % e
