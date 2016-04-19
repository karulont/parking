from testbase import *

class LiftAndMove(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 1, 30, 0)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'c', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'rc', 0] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.lift[(0,0),'rc',t].obj = -1

class LiftAndMoveForced(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 1, 30, 0)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'c', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'rc', 0] == 1)

        mo.addConstr(go[(2,0),'rc',WEST,0] == 1)
        mo.addConstr(vars.lift[(1,0),'rc',2] == 1)
        mo.addConstr(go[(1,0),'cr',WEST,8] == 1)
        mo.addConstr(nstat[(0,0), 'e', 8] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.lift[(0,0),'rc',t].obj = -1

LiftAndMove()
LiftAndMoveForced()
