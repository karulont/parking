import itertools
from consts import *

def makeWhat(K):
    what = set()
    what.add('e')
    what.add('c')
    scj = set()
    for j in range(K):
        scj.add('sc'+str(j))
    what.add('r')
    what.add('rc')
    rscj = set()
    for j in range(K):
        rscj.add('rsc'+str(j))
    what.add('cr')
    scrj = set()
    for j in range(K):
        scrj.add('scr'+str(j))
    what.add('lft')
    slftj = set()
    for j in range(K):
        slftj.add('slft'+str(j))
    what.add('drp')
    sdrpj = set()
    for j in range(K):
        sdrpj.add('sdrp'+str(j))

    what = what.union(scj,rscj,scrj,slftj,sdrpj)
    return what, scj, rscj, scrj, slftj, sdrpj


WEST = 0
NORTH = 1
EAST = 2
SOUTH = 3

def dir2c(d):
    if d == WEST:
        return 'W'
    elif d == NORTH:
        return 'N'
    elif d == EAST:
        return 'E'
    elif d == SOUTH:
        return 'S'

def oppositeDir(d):
    return (d+2) % 4

def edg(node, d):
    assert d >= 0 and d <= 3
    x,y = node
    if d == WEST: # west
        return (x - 1, y)
    elif d == NORTH: # north
        return (x, y - 1)
    elif d == EAST:
        return (x+1, y)
    elif d == SOUTH:
        return (x, y + 1)

def nodes():
    return itertools.product(range(xsize),range(ysize))

def neighbours(node):
    x,y = node
    if x > 0:
        yield (x-1,y)
    if y > 0:
        yield (x,y-1)
    if x < xsize - 1:
        yield (x+1,y)
    if y < ysize - 1:
        yield (x,y+1)

timeiter = range(maxt)
diriter = range(4)

what, scj, rscj, scrj, slftj, sdrpj = makeWhat(K)
moveWhat = set(['r', 'cr', 'rc']).union(rscj, scrj)
liftWhat = set(['rc']).union(rscj)
dropWhat = set(['cr']).union(scrj)
