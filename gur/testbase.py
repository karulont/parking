from gridconfig import *
from situation import *
from model import *
from direction import *

class TestBase:
    def __init__(self, name):
        self.name = name

    def run(self):
        conf = self.conf
        sit = self.situation
        model = GurobiModel(conf)
        model.setSituation(sit)
        model.optimize()
        passed = model.checkStatus(self.name)
        if passed == self.shouldPass:
            print('Test %r successful.' % self.name)
        else:
            print('Test %r failed!' % self.name)

        # for future reference
        self.model = model
