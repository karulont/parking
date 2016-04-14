from gridconfig import *
from situation import *
from model import *
from tests import *
from testbase import all_tests

def main():
    conf = GridConfig(3, 2, 11, 0)
    sit = Situation(conf)
    model = GurobiModel(conf)
    model.setSituation(sit)
    model.optimize()
    model.visualize()

def runTests():
    for t in all_tests:
        t.run()

if __name__ == '__main__':
    runTests()
