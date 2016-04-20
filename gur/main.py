from gridconfig import *
from situation import *
from model import *
from tests import *
from testbase import all_tests
from visualize import Visualize
import sys

def main():
    pass

def runTests():
    for i,t in enumerate(all_tests):
        i = i + 1
        t.run()
        print('%r) Test %r should pass = %r, test passed = %r, checked = %r, overall = %s!'
                % (i,t.name, t.shouldPass, t.passed, t.checked,
                    'success' if t.overall else 'fail'))


    print('\nChoose one to inspect!')
    index = sys.stdin.readline()
    test = all_tests[int(index)-1]
    if test.model.checkStatus():
        Visualize(test.model)
    else:
        test.model.findIIS(test.name)

if __name__ == '__main__':
    runTests()
