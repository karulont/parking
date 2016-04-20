from gridconfig import *
from situation import *
from model import *
from direction import *

class TestBase:
    def __init__(self):
        self.name = type(self).__name__
        all_tests.append(self)

    def run(self):
        model = GurobiModel(self.conf)
        model.setSituation(self.situationObj)
        model.optimize()
        self.passed = model.checkStatus()
        self.checked = False
        if self.passed:
            self.checked = self.checkSolution(model.vars)
            self.overall = self.checked and self.shouldPass
        else:
            self.overall = not self.shouldPass
        # for future reference
        self.model = model

    def checkSolution(self, vars):
        return True

all_tests = list()
