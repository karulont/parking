from testbase import *
from gridconfig_json import *
import json
from os.path import basename, splitext

class Problem(TestBase, Situation):
    def __init__(self, jsonfile, maxt):
        with open(jsonfile, 'r') as f:
            self.jsondata = json.load(f)
            TestBase.__init__(self, log=True)
            self.name = splitext(basename(jsonfile))[0]
            self.conf = GridConfig_json(self.jsondata, maxt)
            Situation.__init__(self, self.conf)
            self.situationObj = self
            self.shouldPass = True

    def situation(self, model, vars):
        mo = model
        specifyNode = self.specifyNode
        nstat = vars.nstat
        go = vars.go

        for x,y in self.conf.nodes():
            mo.addConstr(nstat[(x,y), translate(self.jsondata[3][y][x]), 0] == 1)

    def objective(self, model, vars):
        nstat = vars.nstat
        m = model
        for x,y in self.conf.nodes():
            m.addConstr(nstat[(x,y), translate(self.jsondata[4][y][x]), self.conf.maxt] == 1)
        for t in self.conf.timeiter:
            for x,y in self.conf.nodes():
                w = translate(self.jsondata[4][y][x])
                if w != 'e':
                    nstat[(x,y), w, t].obj = -1

def translate(status):
    if status == '':
        return 'e'
    else:
        return status
