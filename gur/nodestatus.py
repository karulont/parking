class NodeStatuses:
    def __init__(self, K):
        self.K = K
        self.what, self.scj, self.rscj, self.scrj = makeWhat(self.K)
        self.moveWhat = set(['r']).union(self.rscj, self.scrj)
        self.mcWhat = set(['r']).union(self.scrj)
        self.noRobotWhat = set(['e']).union(self.scj)
        self.liftWhat = self.rscj
        self.dropWhat = self.scrj
        self.carsWhat = self.scj
        self.robotsWhat = set(['r']).union(self.rscj)

        self.nodeStatusIO = self.makeNodeStatusIO()
        self.removeRobotWhat = makeRemoveRobotWhat(self.K)
        self.dropWhatHelper = makeDropWhatHelper(self.K)
        self.getMovingComponent = makeGetMovingComponent(self.K)
        self.removeMovingComponent = makeRemoveMovingComponent(self.K)
        self.addMovingComponent = makeAddMovingComponent(self.K)


    def makeNodeStatusIO(self):
        sio = {}
        sio['e'] = (self.moveWhat, set())
        for w in self.carsWhat:
            sio[w] = (self.robotsWhat, set())
        sio['r'] = (set(), set('r'))
        for w in self.liftWhat:
            sio[w] = (set(), set('r'))
        for w in self.dropWhat:
            sio[w] = (set(), set([w]))
        for w in set(['drp','lft']):
            sio[w] = (set(), set())
        return sio

def makeDropWhatHelper(K):
    dwh = {}
    for i in range(K):
        dwh[str(i)+'r'] = 'r'+str(i)
        dwh['r'+str(i)] = str(i)+'r'
    return dwh

def makeWhat(K):
    what = set()
    what.add('e')
    scj = set()
    for j in range(K):
        scj.add(str(j))
    what.add('r')
    rscj = set()
    for j in range(K):
        rscj.add('r'+str(j))
    scrj = set()
    for j in range(K):
        scrj.add(str(j)+'r')
    what.add('lft')
    what.add('drp')

    what = what.union(scj,rscj,scrj)
    return what, scj, rscj, scrj


def makeRemoveRobotWhat(K):
    what = {}
    for j in range(K):
        s = str(j)
        what[s] = s
    what['r'] = 'e'
    for j in range(K):
        s = 'r' + str(j)
        what[s] = str(j)
    for j in range(K):
        s = str(j) + 'r'
        what[s] = 'e'
    return what

def makeGetMovingComponent(K):
    d = {}
    d['r'] = 'r'
    for i in range(K):
        d['r'+str(i)] = 'r'
        d[str(i)+'r'] = str(i)+'r'
    return d

def makeRemoveMovingComponent(K):
    return makeRemoveRobotWhat(K)

def makeAddMovingComponent(K):
    d = {}
    d['e'] = {'r':'r'}
    for i in range(K):
        c = str(i)
        rc = 'r' + str(i)
        cr = str(i) + 'r'
        d['e'][cr] = cr
        d[c] = {'r':rc}
    for i in range(K):
        c = str(i)
        rc = 'r' + str(i)
        for j in range(K):
            rc1 = 'r' + str(j)
            d[c][rc1] = rc
    return d
