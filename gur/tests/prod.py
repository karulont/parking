from testbase import *
from gridconfig_json import *
import json

class Prod(TestBase, Situation):
    def __init__(self, jsonfile, maxt):
        with open(jsonfile, 'r') as f:
            self.jsondata = json.load(f)
            TestBase.__init__(self)
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

def translate(status):
    if status == '':
        return 'e'
    if status == 'r':
        return status
    if status.startswith('r'):
        return 'rsc' + status[1:]
    if status.endswith('r'):
        return 'scr' + status[:-1]
    if status.isnumeric():
        return 'sc' + status
    raise Error(asd)

Prod('../data/marsi3a.json', 40)
