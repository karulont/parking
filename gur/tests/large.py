from testbase import *

class LargeTest(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(4, 2, 10, 0)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        self.setInitialStatus(specifyNode(0,0), 'r')
        self.setInitialStatus(specifyNode(0,1), 'r')
        self.setInitialStatus(specifyNode(1,1), 'r')
        # all other nodes filled with empty
        for v in set(self.conf.nodes()).difference(self.definedNodes):
            self.setInitialStatus(v, 'e')

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.nstat[(3,0),'r',t].obj = -1
            vars.nstat[(3,1),'r',t].obj = -1
            vars.nstat[(2,1),'r',t].obj = -1

class Puzzle(TestBase, Situation):
    def __init__(self):
        TestBase.__init__(self)
        self.conf = GridConfig(3, 3, 15, 1)
        Situation.__init__(self, self.conf)
        self.situationObj = self
        self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        self.setInitialStatus((2,2), 'r')
        self.setInitialStatus((1,1), '0')
        self.setInitialStatus((1,2), '0')
        self.setInitialStatus((1,0), 'r')
        # all other nodes filled with empty
        for v in set(self.conf.nodes()).difference(self.definedNodes):
            self.setInitialStatus(v, 'e')

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.nstat[(1,1),'e',t].obj = -1

LargeTest()
#Puzzle()
