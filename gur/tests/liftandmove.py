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
            vars.nstat[(0,0),'rc',t].obj = -1

    def checkSolution(self, vars):
        nstat = vars.nstat
        conditions = \
            [ nstat[(0,0), 'e', 2].x == 1
            , nstat[(1,0), 'rc', 2].x == 1
            , nstat[(2,0), 'c', 2].x == 1
            , nstat[(1,0), 'cr', 8].x == 1
            , nstat[(0,0), 'cr', 11].x == 1
            ]

        return all(conditions)

class LiftAndMoveForced(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 1, 30, 1)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'sc0', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'rc', 0] == 1)

        mo.addConstr(go[(2,0),'r','W',0] == 1)
        mo.addConstr(vars.lift[(1,0),'rsc0',2] == 1)
        mo.addConstr(go[(1,0),'scr0','W',8] == 1)
        mo.addConstr(nstat[(0,0), 'e', 8] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.lift[(0,0),'rsc0',t].obj = -1

    def checkSolution(self, vars):
        nstat = vars.nstat
        conditions = \
            [ nstat[(0,0), 'e', 2].x == 1
            , nstat[(1,0), 'rsc0', 2].x == 1
            , nstat[(2,0), 'c', 2].x == 1
            , nstat[(1,0), 'scr0', 8].x == 1
            , nstat[(0,0), 'scr0', 11].x == 1
            ]

        return all(conditions)

class LiftAndMove3(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 2, 25, 1)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'sc0', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'rc', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'c', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,1), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,1), 'e', 0] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.nstat[(0,1),'sc0',t].obj = -1

LiftAndMove()
LiftAndMoveForced()
#LiftAndMove3()
