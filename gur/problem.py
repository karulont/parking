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

def translate(status):
    if status == '':
        return 'e'
    else:
        return status
