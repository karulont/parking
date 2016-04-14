from gridconfig import *
from situation import *
from model import *
from testcollision import *

def main():
    conf = GridConfig(3, 2, 11, 0)
    sit = Situation(conf)
    model = GurobiModel(conf)
    model.setSituation(sit)
    model.optimize()
    model.visualize()

def runTests():
    ct = CollisionTest()
    ct.run()
    ct.model.visualize()

if __name__ == '__main__':
    runTests()
