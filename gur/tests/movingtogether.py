from testbase import *

class MovingTogether(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(4, 1, 11, 0)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'r', 0] == 1)
        mo.addConstr(go[(1,0), 'r', WEST, 0] == 1)
        mo.addConstr(go[(2,0), 'r', WEST, 0] == 1)


MovingTogether()
