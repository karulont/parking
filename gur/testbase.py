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
        # for future reference
        self.model = model

all_tests = list()
