from testbase import *

class CollisionTest(TestBase):
    def __init__(self):
        super().__init__()
        self.conf = GridConfig(2, 2, 11, 0)
        self.situation = CollisionSituation(self.conf)
        self.shouldPass = False


class CollisionSituation(Situation):
    def __init__(self, conf):
        super().__init__(conf)

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

class CollisionTest2(TestBase):
    def __init__(self):
        super().__init__()
        self.conf = GridConfig(3, 2, 11, 0)
        self.situation = CollisionSituation2(self.conf)
        self.shouldPass = False


class CollisionSituation2(Situation):
    def __init__(self, conf):
        super().__init__(conf)

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
