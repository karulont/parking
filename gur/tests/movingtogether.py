from testbase import *

class MovingTogether(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 1, 11, 0)
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
        mo.addConstr(go[(1,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(2,0), 'r', 'W', 0] == 1)

    def checkSolution(self, vars):
        nstat = vars.nstat
        conditions = \
            [ nstat[(0,0), 'r', 2].x == 1
            , nstat[(1,0), 'r', 2].x == 1
            , nstat[(2,0), 'e', 2].x == 1
            ]

        return all(conditions)

class MovingTogetherDifferent(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(5, 1, 11, 2)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), '1', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'r0', 0] == 1)
        mo.addConstr(nstat[specifyNode(3,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(4,0), '0r', 0] == 1)
        mo.addConstr(go[(1,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(2,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(3,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(4,0), '0r', 'W', 0] == 1)

    def checkSolution(self, vars):
        nstat = vars.nstat
        conditions = \
            [ nstat[(1,0), 'r', 2].x == 1
            , nstat[(2,0), 'r0', 2].x == 1
            ]

        return all(conditions)

class MovingTogetherBad(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 1, 11, 1)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = False

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'r', 0] == 1)
        mo.addConstr(go[(1,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(2,0), 'r', 'W', 0] == 1)
        mo.addConstr(nstat[(1,0),'r0', 2] == 1)

MovingTogether()
MovingTogetherDifferent()
MovingTogetherBad()
