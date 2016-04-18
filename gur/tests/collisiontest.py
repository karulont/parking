from testbase import *

class CollisionTest(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(2, 2, 11, 0)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = False

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,1), 'r', 0] == 1)
        mo.addConstr(go[(0,1), 'r', EAST, 0] == 1)
        mo.addConstr(go[(1,1), 'r', WEST, 0] == 1)

class CollisionTest2(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 2, 11, 0)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = False

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,1), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,1), 'e', 0] == 1)
        mo.addConstr(go[(2,0), 'r', WEST, 0] == 1)
        mo.addConstr(go[(1,1), 'r', NORTH, 0] == 1)


CollisionTest()
CollisionTest2()
