from gridconfig import *
from situation import *
from model import *
from direction import *
from solution import Solution

class TestBase:
    def __init__(self, log=False):
        self.name = type(self).__name__
        all_tests.append(self)
        self.log=log
        self.initialConf = Solution()
        self.initialConf.full = False
        self.initialConf.maxt = 0
        self.initialConf.nstat = {}
        self.initialConf.command = {}

    def run(self, writeModel=False):
        self.model = GurobiModel(self.conf, log=self.log)
        self.model.addConstraints()
        self.model.setSituation(self.situationObj)
        if writeModel:
            self.model.writeToFile(self.name)
        self.model.optimize()
        self.passed = self.model.checkStatus()
        self.checked = False
        if self.passed:
            self.checked = self.checkSolution(self.model.vars)
            self.overall = self.checked and self.shouldPass
        else:
            self.overall = not self.shouldPass
        self.time = format(self.model.model.getAttr('Runtime'), '.2f')

    def checkSolution(self, vars):
        return True

    def setInitialStatus(self, node, stat):
        vars =  self.model.vars
        mo = self.model.model
        mo.addConstr(vars.nstat[node, stat, 0] == 1)
        self.initialConf.nstat[node,0] = stat
        self.initialConf.command[node,0] = str(node)

    def getInitialStatus(self):
        self.initialConf.nodes = set(self.conf.nodes())
        self.initialConf.edges = set(self.conf.edges())
        return self.initialConf

all_tests = list()
