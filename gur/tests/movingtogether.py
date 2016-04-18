from testbase import *

class MovingTogether(TestBase):
    def __init__(self):
        super().__init__()
        self.conf = GridConfig(4, 1, 11, 0)
        self.situation = MovingSituation(self.conf)
        self.shouldPass = True


class MovingSituation(Situation):
    def __init__(self, conf):
        super().__init__(conf)

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
