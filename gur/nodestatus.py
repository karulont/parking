class NodeStatuses:
    def __init__(self, K):
        self.K = K
        self.what, self.scj, self.rscj, self.scrj = makeWhat(self.K)
        self.moveWhat = set(['r', 'cr', 'rc']).union(self.rscj, self.scrj)
        self.mcWhat = set(['r', 'cr']).union(self.scrj)
        self.noRobotWhat = set(['e', 'c']).union(self.scj)
        self.liftWhat = set(['rc']).union(self.rscj)
        self.dropWhat = set(['cr']).union(self.scrj)
        self.carsWhat = set(['c']).union(self.scj)
        self.robotsWhat = set(['r','rc']).union(self.rscj)

        self.nodeStatusIO = self.makeNodeStatusIO()
        self.removeRobotWhat = makeRemoveRobotWhat(self.K)
        self.dropWhatHelper = makeDropWhatHelper(self.K)
        self.usPlusWs = makeUsPlusWs(self.K)
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
    dwh['cr'] = 'rc'
    dwh['rc'] = 'cr'
    for i in range(K):
        dwh['scr'+str(i)] = 'rsc'+str(i)
        dwh['rsc'+str(i)] = 'scr'+str(i)
    return dwh

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
    what.add('drp')

    what = what.union(scj,rscj,scrj)
    return what, scj, rscj, scrj


def makeRemoveRobotWhat(K):
    what = {}
    for j in range(K):
        s = 'sc' + str(j)
        what[s] = s
    what['r'] = 'e'
    what['rc'] = 'c'
    for j in range(K):
        s = 'rsc' + str(j)
        what[s] = 'sc' + str(j)
    what['cr'] = 'e'
    for j in range(K):
        s = 'scr' + str(j)
        what[s] = 'e'
    return what

def makeUsPlusWs(K):
    what = {}
    what['e'] = {'r':'r', 'rc':'r', 'cr':'cr'}
    what['c'] = {'r':'rc', 'rc':'rc'}
    for i in range(K):
        c = 'sc' + str(i)
        rc = 'rsc' + str(i)
        cr = 'scr' + str(i)
        what['e'][rc] = 'r'
        what['e'][cr] = cr
        what['c'][rc] = 'rc'
        what[c] = {'r':rc, 'rc':rc}
    for i in range(K):
        c = 'sc' + str(i)
        rc = 'rsc' + str(i)
        for j in range(K):
            rc1 = 'rsc' + str(j)
            what[c][rc1] = rc

    return what

def makeGetMovingComponent(K):
    d = {}
    d['r'] = 'r'
    d['rc'] = 'r'
    d['cr'] = 'cr'
    for i in range(K):
        d['rsc'+str(i)] = 'r'
        d['scr'+str(i)] = 'scr'+str(i)
    return d

def makeRemoveMovingComponent(K):
    return makeRemoveRobotWhat(K)

def makeAddMovingComponent(K):
    d = {}
    d['e'] = {'r':'r', 'cr':'cr'}
    d['c'] = {'r':'rc'}
    for i in range(K):
        c = 'sc' + str(i)
        rc = 'rsc' + str(i)
        cr = 'scr' + str(i)
        d['e'][cr] = cr
        d['c'][rc] = 'rc'
        d[c] = {'r':rc, 'rc':rc}
    for i in range(K):
        c = 'sc' + str(i)
        rc = 'rsc' + str(i)
        for j in range(K):
            rc1 = 'rsc' + str(j)
            d[c][rc1] = rc
    return d
