from testbase import *
from gridconfig_json import *
import json
from os.path import basename, splitext

class Problem(TestBase, Situation):
    def __init__(self, jsonfile, maxt, terminalConst, objective):
        with open(jsonfile, 'r') as f:
            self.jsondata = json.load(f)
            TestBase.__init__(self, log=True)
            self.name = splitext(basename(jsonfile))[0]
            self.conf = GridConfig_json(self.jsondata, maxt)
            Situation.__init__(self, self.conf)
            self.situationObj = self
            self.shouldPass = True

            self.terminalConst = terminalConst

            if objective == 'timeonly':
                self.objective = self.objectiveDiff
            elif objective == 'energy':
                self.objective = self.objectiveEnergy
            elif objective == 'full':
                self.objective = self.objectiveFull
            elif objective == 'prog':
                self.objective = self.objectiveProgressive
            else:
                self.objective = self.objectiveNone

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go
        if self.terminalConst:
            self.constrainTerminalStatus(mo,nstat)

        for x,y in self.conf.nodes():
            mo.addConstr(nstat[(x,y), translate(self.jsondata[3][y][x]), 0] == 1)

    def constrainTerminalStatus(self, m, nstat):
        print('Adding constraints for terminal status')
        for x,y in self.conf.nodes():
            m.addConstr(nstat[(x,y), translate(self.jsondata[4][y][x]), self.conf.maxt] == 1)

    def objectiveNone(self, model, vars):
        print('Using no objective function')
        return

    def objectiveDiff(self, model, vars):
        print('Using timeonly objective function')
        nstat = vars.nstat
        m = model
        for t in self.conf.timeiter:
            for x,y in self.conf.nodes():
                w = translate(self.jsondata[4][y][x])
                if w != 'e':
                    nstat[(x,y), w, t].obj = -1

    def objectiveEnergy(self, model, vars):
        print('Using energy objective function')
        for v in vars.go:
            vars.go[v].obj = 0.02
        for v in vars.cont:
            vars.cont[v].obj = 0.01
        for v in vars.stop:
            vars.stop[v].obj = 0.02
        for v in vars.lift:
            vars.lift[v].obj = 0.04
        for v in vars.drop:
            vars.drop[v].obj = 0.01

    def objectiveFull(self, model, vars):
        print('Using full objective function')
        self.objectiveDiff(model, vars)
        self.objectiveEnergy(model, vars)

    def objectiveProgressive(self, model, vars):
        print('Using progressive energy objective function')
        def timeCost(t):
            return 1 + (t / self.conf.maxt)

        for v in vars.go:
            t = v[3]
            vars.go[v].obj = 0.2 * timeCost(t)
        for v in vars.cont:
            t = v[3]
            vars.cont[v].obj = 0.1 * timeCost(t)
        for v in vars.stop:
            t = v[3]
            vars.stop[v].obj = 0.2 * timeCost(t)
        for v in vars.lift:
            t = v[2]
            vars.lift[v].obj = 0.4 * timeCost(t)
        for v in vars.drop:
            t = v[2]
            vars.drop[v].obj = 0.1 * timeCost(t)

        t = self.conf.maxt

        for x,y in self.conf.nodes():
            for w in self.conf.whats.what:
                wp = translate(self.jsondata[4][y][x])
                if w != wp:
                    vars.nstat[(x,y), w, t].obj = 10

def translate(status):
    if status == '':
        return 'e'
    else:
        return status
