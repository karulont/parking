import itertools
from direction import *

class Vars():

    def __init__(self, conf, addVar):
        nstat = {}
        occu = {}

        whats = conf.whats

        for (x,y),t in itertools.product(conf.nodes(), conf.timeiter):
            for w in whats.what:
                addVar(nstat, "nstat", ((x,y), w, t))

        for e,t in itertools.product(conf.edges(), conf.timeiter):
            addVar(occu, "occu", (e,t))

        # add "decision" variables
        go = {}
        stop = {}
        cont = {}
        lift = {}
        drop = {}

        for v in conf.nodes():
            for w,t in itertools.product(whats.liftWhat, conf.timeiter):
                addVar(lift, "lift", (v,w,t))
            for w,t in itertools.product(whats.dropWhat, conf.timeiter):
                addVar(drop, "drop", (v,w,t))
        for e,w,t in itertools.product(conf.edges(), whats.mcWhat, conf.timeiter):
            d = getEdgeDir(e)
            v,_ = e
            addVar(go, "go", (v,w,d,t))
            addVar(stop, "stop", (v,w,d,t))
            addVar(cont, "cont", (v,w,d,t))

        # assing to instance
        self.nstat = nstat
        self.occu = occu
        self.go = go
        self.stop = stop
        self.cont = cont
        self.lift = lift
        self.drop = drop

