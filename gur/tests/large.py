from testbase import *

class LargeTest(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 3, 30, 2)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(1,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,2), 'r', 0] == 1)
        # all other nodes filled with empty
        for v in set(self.conf.nodes()).difference(self.definedNodes):
            mo.addConstr(nstat[v, 'e', 0] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.nstat[(2,0),'r',t].obj = -1
            vars.nstat[(1,1),'r',t].obj = -1

LargeTest()
