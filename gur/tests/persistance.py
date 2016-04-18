from testbase import *

class PersistanceNoRobots(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 1, 30, 0)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = False

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'c', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'c', 0] == 1)

        mo.addConstr(nstat[(0,0), 'r', 20] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.nstat[(0,0),'r',t].obj = -4
            for e in self.conf.edges():
                vars.occu[e,t].obj = 1;

PersistanceNoRobots()

