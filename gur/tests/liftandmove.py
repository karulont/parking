from testbase import *

class LiftAndMove(TestBase):
    def __init__(self):
        super().__init__()
        self.conf = GridConfig(3, 1, 20, 0)
        self.situation = LiftAndMoveSit(self.conf)
        self.shouldPass = True


class LiftAndMoveSit(Situation):
    def __init__(self, conf):
        super().__init__(conf)

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'c', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'r', 0] == 1)

        mo.addConstr(go[(2,0),'r',WEST,0] == 1)
        #mo.addConstr(lift[(1,0),'r',WEST,0] == 1)

    def objective(self, model, vars):
        for t in self.conf.timeiter:
            vars.nstat[(0,0),'c',t].obj = -1

LiftAndMove()
