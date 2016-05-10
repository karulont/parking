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
        mo.addConstr(go[(0,1), 'r', 'E', 0] == 1)
        mo.addConstr(go[(1,1), 'r', 'W', 0] == 1)

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
        mo.addConstr(go[(2,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(1,1), 'r', 'N', 0] == 1)

class CollisionWithSpecial(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(2, 2, 16, 2)
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
        mo.addConstr(nstat[specifyNode(0,1), 'scr0', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,1), 'scr1', 0] == 1)
        mo.addConstr(go[(0,1), 'scr0', 'E', 0] == 1)
        mo.addConstr(go[(1,1), 'scr1', 'W', 0] == 1)

class CollisionTestOrthogonal(TestBase, Situation):
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
        mo.addConstr(nstat[specifyNode(1,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,1), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,1), 'e', 0] == 1)
        mo.addConstr(go[(1,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(1,1), 'r', 'N', 0] == 1)

class CollisionWithItself(TestBase, Situation):
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
        mo.addConstr(nstat[specifyNode(1,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'r', 0] == 1)
        mo.addConstr(go[(2,0), 'r', 'W', 0] == 1)
        mo.addConstr(go[(1,0), 'r', 'E', 2] == 1)

CollisionTest()
CollisionTest2()
CollisionWithSpecial()
CollisionTestOrthogonal()
CollisionWithItself()
