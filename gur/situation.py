import itertools
from direction import *

class Situation():

    def __init__(self, conf):
        self.definedNodes = set()
        self.conf = conf

    def specifyNode(self, x, y):
        v = (x,y)
        assert v not in self.definedNodes
        self.definedNodes.add(v)
        return v

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat


        # initial configuration

        # robot
        mo.addConstr(nstat[specifyNode(0,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,1), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,1), 'r', 0] == 1)
        #mo.addConstr(drop[(0,0), 'cr', 0] == 1)

        """
        # do not allow lift and drop
        for v,t in itertools.product(nodes(), timeiter):
            s = [nstat[v,w,t] for w in ('lft','drp')]
            mo.addConstr(quicksum(s) == 0)
        """

        """
        # special cars
        mo.addConstr(nstat[specifyNode(2,2), 'sc0', 0] == 1)
        mo.addConstr(nstat[specifyNode(3,3), 'sc1', 0] == 1)
        # empty places
        mo.addConstr(nstat[specifyNode(2,1), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'e', 0] == 1)
        # all other nodes filled with anonymous cars
        for v in set(nodes()).difference(definedNodes):
            mo.addConstr(nstat[v, 'c', 0] == 1)
        """

    def objective(self, model, vars):
        # add objective
        costvars = set()
        
        v = (0,0) # node where to dropoff cars
        for w,t in itertools.product(self.conf.whats.scj, self.conf.timeiter):
            #costvars.add(nstat[v,w,t])
            pass
        # drop car TODO: temporary
        for t in self.conf.timeiter:
            costvars.add(vars.nstat[v,'r',t])
        for var in costvars:
            var.obj = -1


