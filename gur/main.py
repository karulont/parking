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
    print(args)
    test = Problem(args.file, args.tmax, args.constr, args.objective)
    test.run(args.write)
    if test.model.checkStatus():
        sol = test.model.extractSolution()
        with open(test.name + ('-%d' % args.tmax) + '.sol', 'wb') as f:
            pickle.dump(sol,f)
        Visualize(sol)

def view(args):
    with open(args.file, 'rb') as f:
        sol = pickle.load(f)
        Visualize(sol)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IP model for parking problem')
    subparsers = parser.add_subparsers()
    solveParser = subparsers.add_parser('solve', description='solve a problem')
    solveParser.add_argument('-c', dest='constr', action='store_true', default=False,
            help='use constraints to fix terminal status')
    solveParser.add_argument('-o','--objective', default='full',
            choices=['none', 'timeonly', 'energy', 'full', 'prog'],
            help='use the specified objective function')
    solveParser.add_argument('-w', dest='write', action='store_true', default=False,
            help='write problem to file')
    solveParser.add_argument('file', help='problem file')
    solveParser.add_argument('tmax', type=int, help='Number of timesteps in the model')
    solveParser.set_defaults(func=problem)
    viewParser = subparsers.add_parser('view', description='view solution')
    viewParser.add_argument('file', help='problem file')
    viewParser.set_defaults(func=view)
    testParser = subparsers.add_parser('test', description='run tests')
    testParser.set_defaults(func=runTests)
    parser.set_defaults(func=lambda x: parser.print_help())
    args = parser.parse_args()
    args.func(args)
