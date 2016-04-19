from gridconfig import *
from situation import *
from model import *
from tests import *
from testbase import all_tests
from visualize import Visualize
import sys

def main():
    conf = GridConfig(3, 2, 11, 0)
    sit = Situation(conf)
    model = GurobiModel(conf)
    model.setSituation(sit)
    model.optimize()
    model.visualize()

def runTests():
    for i,t in enumerate(all_tests):
        i = i + 1
        t.run()
        print('%r) Test %r should pass = %r, test passed = %r, overall = %s!'
                % (i,t.name, t.shouldPass, t.passed,
                    'success' if t.passed == t.shouldPass else 'fail'))


    print('\nChoose one to inspect!')
    index = sys.stdin.read(1)
    test = all_tests[int(index)-1]
    if test.model.checkStatus():
        Visualize(test.model)
    else:
        test.model.findIIS(test.name)

if __name__ == '__main__':
    runTests()
