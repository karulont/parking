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
        pass

    def objective(self, model, vars):
        pass
