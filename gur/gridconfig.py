import itertools
from direction import *
from util import *

class GridConfig:
    def __init__(self, xsize, ysize, maxt, K):
        self.xsize = xsize
        self.ysize = ysize
        self.maxt = maxt
        self.K = K

        self.what, self.scj, self.rscj, self.scrj, self.slftj, self.sdrpj = self._makeWhat()
        self.moveWhat = set(['r', 'cr', 'rc']).union(self.rscj, self.scrj)
        self.liftWhat = set(['rc']).union(self.rscj)
        self.dropWhat = set(['cr']).union(self.scrj)
        self.timeiter = range(maxt)

        self.nodeStatusIO = self.makeNodeStatusIO()
        self.dropWhatHelper = self.makeDropWhatHelper()

        # set of nodes and edges for fast in check
        self.nodeSet = set(self.nodes())
        self.edgeSet = set(self.edges())

    def makeDropWhatHelper(self):
        dwh = {}
        dwh['cr'] = 'rc'
        dwh['rc'] = 'cr'
        for i in range(self.K):
            dwh['scr'+str(i)] = 'rsc'+str(i)
            dwh['rsc'+str(i)] = 'scr'+str(i)
        return dwh

    def makeNodeStatusIO(self):
        sio = {}
        sio['e'] = (self.moveWhat, set())
        for w in set('c').union(self.scj):
            sio[w] = (set(['r','rc']).union(self.rscj), set())
        sio['r'] = (set(), set('r'))
        for w in self.liftWhat:
            sio[w] = (set(), set('r'))
        for w in self.dropWhat:
            sio[w] = (set(), set([w]))
        for w in set(['lft']).union(self.slftj):
            sio[w] = (set(), set())
        for w in set(['drp']).union(self.sdrpj):
            sio[w] = (set(), set())
        return sio

    def _makeWhat(self):
        what = set()
        what.add('e')
        what.add('c')
        scj = set()
        for j in range(self.K):
            scj.add('sc'+str(j))
        what.add('r')
        what.add('rc')
        rscj = set()
        for j in range(self.K):
            rscj.add('rsc'+str(j))
        what.add('cr')
        scrj = set()
        for j in range(self.K):
            scrj.add('scr'+str(j))
        what.add('lft')
        slftj = set()
        for j in range(self.K):
            slftj.add('slft'+str(j))
        what.add('drp')
        sdrpj = set()
        for j in range(self.K):
            sdrpj.add('sdrp'+str(j))

        what = what.union(scj,rscj,scrj,slftj,sdrpj)
        return what, scj, rscj, scrj, slftj, sdrpj

    def removeRobotWhat(self, what):
        if what in self.liftWhat:
            return what[1:]
        else:
            raise Error('asd')

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
        return t+dt < self.maxt and t+dt >= 0

