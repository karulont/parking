import itertools
from direction import *
from nodestatus import *

class GridConfig:
    def __init__(self, xsize, ysize, maxt, K):
        self.xsize = xsize
        self.ysize = ysize
        self.maxt = maxt
        self.K = K
        self.timeiter = range(maxt+1)

        self.whats = NodeStatuses(self.K)

        # set of nodes and edges for fast in check
        self.nodeSet = set(self.nodes())
        self.edgeSet = set(self.edges())

    def nodes(self):
        return itertools.product(range(self.xsize),range(self.ysize))

    def edges(self):
        for u in self.nodes():
            for v in self.neighbours(u):
                if v in self.nodeSet:
                    yield (u,v)

    def neighbours(self, node):
        x,y = node
        if x > 0:
            yield (x-1,y)
        if y > 0:
            yield (x,y-1)
        if x < self.xsize - 1:
            yield (x+1,y)
        if y < self.ysize - 1:
            yield (x,y+1)

    def edg(self, node, d):
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

    def checkNode(self, node):
        return node in self.nodeSet

    def checkEdge(self, edge):
        return edge in self.edgeSet

    def checkTime(self, t, dt):
        return t+dt <= self.maxt and t+dt >= 0

