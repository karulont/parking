class NodeStatuses:
    def __init__(self, K):
        self.K = K
        self.what, self.scj, self.rscj, self.scrj, self.slftj, self.sdrpj = makeWhat(self.K)
        self.moveWhat = set(['r', 'cr', 'rc']).union(self.rscj, self.scrj)
        self.liftWhat = set(['rc']).union(self.rscj)
        self.dropWhat = set(['cr']).union(self.scrj)
        self.carsWhat = set(['c']).union(self.scj)
        self.robotsWhat = set(['r','rc']).union(self.rscj)
        self.allLiftWhat = set(['lft']).union(self.slftj)
        self.allDropWhat = set(['drp']).union(self.sdrpj)

        self.nodeStatusIO = self.makeNodeStatusIO()
        self.removeRobotWhat = makeRemoveRobotWhat(self.K)
        self.dropWhatHelper = makeDropWhatHelper(self.K)
        self.usPlusWs = makeUsPlusWs(self.K)

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
        for w in self.allLiftWhat:
            sio[w] = (set(), set())
        for w in self.allDropWhat:
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
    slftj = set()
    for j in range(K):
        slftj.add('slft'+str(j))
    what.add('drp')
    sdrpj = set()
    for j in range(K):
        sdrpj.add('sdrp'+str(j))

    what = what.union(scj,rscj,scrj,slftj,sdrpj)
    return what, scj, rscj, scrj, slftj, sdrpj


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
    whate = {}
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
