from testbase import *

class PersistenceNoRobots(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 1, 30, 1)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = False

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        self.setInitialStatus((0,0), 'e')
        self.setInitialStatus((1,0), '0')
        self.setInitialStatus((2,0), '0')

        mo.addConstr(nstat[(0,0), 'r', 20] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.nstat[(0,0),'r',t].obj = -4
            vars.nstat[(1,0),'r',t].obj = -4
            for e in self.conf.edges():
                vars.occu[e,t].obj = -1;

PersistenceNoRobots()

