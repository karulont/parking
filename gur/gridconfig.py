import itertools
from direction import *
from nodestatus import *

class GridConfig:
    def __init__(self, xsize, ysize, maxt, K):
        self.xsize = xsize
        self.ysize = ysize
        self.maxt = maxt
        self.K = K
        self.timeLimit = None
        self.timeiter = range(maxt+1)

        self.whats = NodeStatuses(self.K)

        # set of nodes and edges for fast in check
        self.nodeSet = set(self.nodes())
        self.edgeSet = set(self.edges())

    def nodes(self):
        return itertools.product(range(self.xsize),range(self.ysize))

    def edges(self):
        for u in self.nodes():
            for v in neighbours(u):
                if v in self.nodeSet:
                    yield (u,v)

    def checkNode(self, node):
        return node in self.nodeSet

    def checkEdge(self, edge):
        return edge in self.edgeSet

    def checkTime(self, t, dt):
        return t+dt <= self.maxt and t+dt >= 0

