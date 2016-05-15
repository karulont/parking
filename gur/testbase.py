from gridconfig import *
from situation import *
from model import *
from direction import *

class TestBase:
    def __init__(self, log=False):
        self.name = type(self).__name__
        all_tests.append(self)
        self.log=log

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

all_tests = list()
