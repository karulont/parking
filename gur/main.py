from gridconfig import *
from situation import *
from model import *
from tests import *
from testbase import all_tests
from visualize import Visualize
from problem import *
import sys
import argparse
import pickle

def runTests(args=None):
    for i,t in enumerate(all_tests):
        i = i + 1
        t.run()
        print('%r) Test %r (%r s) should pass = %r, test passed = %r, checked = %r, overall = %s!'
                % (i,t.name, t.time, t.shouldPass, t.passed, t.checked,
                    'success' if t.overall else 'fail'))

    print('\nChoose one to inspect!')
    index = sys.stdin.readline()
    test = all_tests[int(index)-1]
    if test.model.checkStatus():
        Visualize(test.model.extractSolution())
    else:
        test.model.findIIS(test.name)

def problem(args):
    test = Problem(args.file, args.tmax, args.constr, args.objective, timeLimit=args.timeLimit)
    test.run(args.write)
    if test.model.checkStatus():
        sol = test.model.extractSolution()
        with open('solution.sol', 'wb') as f:
            pickle.dump(sol,f)

def view(args):
    with open(args.file, 'rb') as f:
        sol = pickle.load(f)
        Visualize(sol)

class Mockargs:
    pass

if __name__ == '__main__':
    args = Mockargs()
    args.objective = 'prog'
    args.constr = False
    args.write = False
    args.timeLimit = int(sys.argv[1])
    args.file = sys.argv[2]
    args.tmax = int(sys.argv[3])
    problem(args)
