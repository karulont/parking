from gurobipy import *
import itertools
import sys
from util import *

from vars import *

class GurobiModel:

    def __init__(self, conf):

        self.conf = conf
        self.initialModel = Model("parking")
        self.model = self.initialModel

        def addFunc(set, setname, key):
            set[key] = self.model.addVar(vtype = GRB.BINARY,
                    name = setname + str(key).replace(" ",""))

        self.vars = Vars(conf, addFunc)
        self.model.update()
        self.addConstraints()

    def addConstraints(self):
        mo = self.initialModel;
        self.model = self.initialModel
        # reference grid conf stuff for easier access
        xsize = self.conf.xsize
        ysize = self.conf.ysize
        maxt = self.conf.maxt

        nodes = self.conf.nodes
        edg = self.conf.edg
        neighbours = self.conf.neighbours
        timeiter = self.conf.timeiter
        what = self.conf.what
        scj = self.conf.scj
        rscj = self.conf.rscj
        scrj = self.conf.scrj
        slftj = self.conf.slftj
        sdrpj = self.conf.sdrpj
        moveWhat = self.conf.moveWhat 
        liftWhat = self.conf.liftWhat 
        dropWhat = self.conf.dropWhat 

        checkNode = self.conf.checkNode
        checkEdge = self.conf.checkEdge
        checkTime = self.conf.checkTime

        # reference variables for easier access
        nstat = self.vars.nstat
        occu = self.vars.occu
        go = self.vars.go
        stop = self.vars.stop
        cont = self.vars.cont
        lift = self.vars.lift
        drop = self.vars.drop

        mo.update()
        print('Adding constraints')

        # important: at time 0 everything is still so do not allow continue or stop
        for u,w,d in itertools.product(self.conf.nodes(), self.conf.moveWhat, diriter):
            v = self.conf.edg(u,d);
            if not self.conf.checkNode(v):
                # Off grid in that direction
                continue
            mo.addConstr(cont[u,w,d,0] == 0);
            mo.addConstr(stop[u,w,d,0] == 0);


        # some ideas for good constraints:
        #  * count the number of cars, make sure that it stays same
        #  * count the number of robots, make sure that it stays same

        # one status per node per timestep
        for v,t in itertools.product(nodes(), timeiter):
            s = [nstat[v,w,t] for w in what]
            mo.addConstr(quicksum(s) == 1)

        # more than one vehicle cannot arrive at same node
        for v,t in itertools.product(nodes(), timeiter):
            s = []
            for u in neighbours(v):
                s.append(occu[normalizeEdge((u,v)),t])
            mo.addConstr(quicksum(s) <= 1)

        # orthogonal directions
        for v,d,t in itertools.product(nodes(), diriter, timeiter):
            s = []
            u = edg(v,d)
            try:
                s.append(occu[u,v,t])
                try:
                    s.append(occu[v,edg(v,(d - 1) % 4),t])
                except KeyError:
                    pass
                try:
                    s.append(occu[v,edg(v,(d + 1) % 4),t])
                except KeyError:
                    pass
                mo.addConstr(quicksum(s) <= 1)
            except KeyError:
                pass

        # no more than one decision per node per timestep
        for v,t in itertools.product(nodes(), timeiter):
            s = []
            for d,w in itertools.product(diriter, moveWhat):
                s.append(go[v,w,d,t])
                s.append(stop[v,w,d,t])
                s.append(cont[v,w,d,t])
            for w in liftWhat:
                s.append(lift[v,w,t])
            for w in dropWhat:
                s.append(drop[v,w,t])
            mo.addConstr(quicksum(s) <= 1)

        # robot movements
        for u,w,d in itertools.product(nodes(), moveWhat, diriter):
            v = edg(u,d);
            vp = edg(v,d);
            if not checkNode(v):
                # Off grid in that direction
                continue
            for t in timeiter:
                mo.addConstr(go[u,w,d,t] - nstat[u,w,t] <= 0)
                if (d == NORTH or d == SOUTH) and (w == 'cr' or w in scrj):
                    # movement is slow and length is long
                    if checkTime(t,5):
                        e = normalizeEdge((u,v))
                        mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+4] -cont[u,w,d,t+4] +nstat[u,w,t] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+1] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+2] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+3] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+4] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,w,t+5] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+1] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+2] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+3] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+4] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,'e',t] <= 1)
                        mo.addConstr(stop[u,w,d,t+4] -nstat[u,w,t] <= 0)
                        mo.addConstr(cont[u,w,d,t+4] -nstat[u,w,t] <= 0)
                        mo.addConstr(stop[u,w,d,t+4] -nstat[u,w,t+4] <= 0)
                        mo.addConstr(cont[u,w,d,t+4] -nstat[u,w,t+4] <= 0)
                        if not checkNode(vp):
                            mo.addConstr(cont[u,w,d,t+4] == 0)
                        elif checkTime(t,8):
                            mo.addConstr(cont[v,w,d,t+8] + stop[v,w,d,t+8] -cont[u,w,d,t+4] == 0)
                    if checkTime(t,-4):
                        mo.addConstr(cont[u,w,d,t] +stop[u,w,d,t] -go[u,w,d,t-4] -cont[u,w,d,t-4] == 0)
                    elif t < 4:
                        # disable cont or stop because could not be given
                        mo.addConstr(cont[u,w,d,t] == 0)
                        mo.addConstr(stop[u,w,d,t] == 0)
                elif (d == EAST or d == WEST) and (w == 'r' or w == 'rc' or w in rscj):
                    ws,we = whatSE(w)
                    # movement fast and lenght short
                    if checkTime(t,2):
                        e = normalizeEdge((u,v))
                        mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+1] -cont[u,w,d,t+1] +nstat[u,w,t] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+1] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,w,t+2] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+1] <= 1)
                        mo.addConstr(stop[u,w,d,t+1] -nstat[u,w,t] <= 0)
                        mo.addConstr(cont[u,w,d,t+1] -nstat[u,w,t] <= 0)
                        mo.addConstr(stop[u,w,d,t+1] -nstat[u,w,t+1] <= 0)
                        mo.addConstr(cont[u,w,d,t+1] -nstat[u,w,t+1] <= 0)
                        if not checkNode(vp):
                            mo.addConstr(cont[u,w,d,t+1] == 0)
                        elif checkTime(t,2):
                            mo.addConstr(cont[vp,w,d,t+2] + stop[vp,w,d,t+2] -cont[u,w,d,t+1] == 0)
                    if checkTime(t,-1):
                        mo.addConstr(cont[u,w,d,t] +stop[u,w,d,t] -go[u,w,d,t-1] -cont[u,w,d,t-1] == 0)
                    elif t < 1:
                        # disable cont or stop because could not be given
                        mo.addConstr(cont[u,w,d,t] == 0)
                        mo.addConstr(stop[u,w,d,t] == 0)
                else:
                    # movement fast and long or movement slow and short
                    if checkTime(t,3):
                        e = normalizeEdge((u,v))
                        mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+2] -cont[u,w,d,t+2] +nstat[u,w,t] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+1] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+2] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,w,t+3] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+1] <= 1)
                        mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+2] <= 1)
                        mo.addConstr(stop[u,w,d,t+2] -nstat[u,w,t] <= 0)
                        mo.addConstr(cont[u,w,d,t+2] -nstat[u,w,t] <= 0)
                        mo.addConstr(stop[u,w,d,t+2] -nstat[u,w,t+2] <= 0)
                        mo.addConstr(cont[u,w,d,t+2] -nstat[u,w,t+2] <= 0)
                        if not checkNode(vp):
                            mo.addConstr(cont[u,w,d,t+2] == 0)
                        elif checkTime(t,4):
                            mo.addConstr(cont[v,w,d,t+4] + stop[v,w,d,t+4] -cont[u,w,d,t+2] == 0)
                    if checkTime(t,-2):
                        mo.addConstr(cont[u,w,d,t] +stop[u,w,d,t] -go[u,w,d,t-2] -cont[u,w,d,t-2] == 0)
                    elif t < 2:
                        # disable cont or stop because could not be given
                        mo.addConstr(cont[u,w,d,t] == 0)
                        mo.addConstr(stop[u,w,d,t] == 0)

        # node status changes constraints for empty node
        for u,t in itertools.product(nodes(), timeiter):
            if checkTime(t,1):
                contOrStop = []
                gos = []
                for d,w in itertools.product(diriter, moveWhat):
                    v = edg(u,d);
                    if checkNode(v):
                        contOrStop.append(cont[v,w,oppositeDir(d), t])
                        contOrStop.append(stop[v,w,oppositeDir(d), t])
                        gos.append(stop[u,w,d,t]);
                        gos.append(cont[u,w,d,t]);

                SCS0 = quicksum(contOrStop)
                SG0 = quicksum(gos)
                mo.addConstr(nstat[u,'e',t] -nstat[u,'e',t+1] -SCS0 +SG0 == 0)

                mo.addConstr(-nstat[u,'e',t+1] -SCS0 +SG0 <= 0)
                mo.addConstr(-nstat[u,'e',t+1] <= 0)
                mo.addConstr(-SCS0 <= 0)
                mo.addConstr(-SG0 <= 0)
                mo.addConstr(nstat[u,'e',t+1] +SCS0 <= 1)

        # node status changes for car nodes
        for u,t in itertools.product(nodes(), timeiter):
            if checkTime(t,1):
                pass


        # dropping time constraint
        for v,w,t in itertools.product(nodes(), dropWhat, timeiter):
            if checkTime(t,2):
                mo.addConstr(-nstat[v,'cr',t+1] +drop[v,'cr',t] <= 0)
                mo.addConstr(-nstat[v,'cr',t] +drop[v,'cr',t] <= 0)
                mo.addConstr(nstat[v,'cr',t] +nstat[v,'rc',t+2] -drop[v,'cr',t] <= 1)
                mo.addConstr(nstat[v,'cr',t+1] -drop[v,'cr',t] -nstat[v,'cr',t+2] <= 0)
                mo.addConstr(-nstat[v,'rc',t+2] +drop[v,'cr',t] <= 0)

        # lifting time constraint
        for v,w,t in itertools.product(nodes(), dropWhat, timeiter):
            if checkTime(t,2):
                mo.addConstr(-nstat[v,'cr',t+1] +drop[v,'cr',t] <= 0)
                mo.addConstr(-nstat[v,'cr',t] +drop[v,'cr',t] <= 0)
                mo.addConstr(nstat[v,'cr',t] +nstat[v,'rc',t+2] -drop[v,'cr',t] <= 1)
                mo.addConstr(nstat[v,'cr',t+1] -drop[v,'cr',t] -nstat[v,'cr',t+2] <= 0)
                mo.addConstr(-nstat[v,'rc',t+2] +drop[v,'cr',t] <= 0)


        mo.update()


    def optimize(self):
        self.model.optimize()

    def setSituation(self, sit):
        # self.model = self.initialModel.copy()
        sit.situation(self.model, self.vars)
        sit.objective(self.model, self.vars)
        self.model.update()

    def visualize(self):
        # quick reference
        nstat = self.vars.nstat
        occu = self.vars.occu
        go = self.vars.go
        stop = self.vars.stop
        cont = self.vars.cont
        lift = self.vars.lift
        drop = self.vars.drop

        what = self.conf.what
        moveWhat = self.conf.moveWhat 
        liftWhat = self.conf.liftWhat 
        dropWhat = self.conf.dropWhat 

        if self.model.status == GRB.status.OPTIMAL:
            #print the solution
            for t in self.conf.timeiter:
                print("timestep {0}:".format(t))
                for y in range(self.conf.ysize):
                    s = ''
                    for x in range(self.conf.xsize):
                        for w in what:
                            if nstat[(x,y),w,t].x == 1:
                                s += '{:^5}'.format(w)
                                break
                    s += '\t\t'
                    for x in range(self.conf.xsize):
                        v = (x,y)
                        decision = '{:^10}'.format('_')
                        for d,w in itertools.product(diriter, moveWhat):
                            td = dir2c(d)
                            if go[v,w,d,t].x == 1:
                                decision = '{:^10}'.format('GO_{}{}'.format(td,w))
                            if stop[v,w,d,t].x == 1:
                                decision = '{:^10}'.format('STOP_{}{}'.format(td,w))
                            if cont[v,w,d,t].x == 1:
                                decision = '{:^10}'.format('CONT_{}{}'.format(td,w))
                        for w in liftWhat:
                            if lift[v,w,t].x == 1:
                                decision = '{:^10}'.format('LIFT')
                        for w in dropWhat:
                            if drop[v,w,t].x == 1:
                                decision = '{:^10}'.format('DROP')

                        s += decision
                    s += '\t\t'
                    for x in range(self.conf.xsize):
                        u = (x,y)
                        ur = (x+1,y)
                        ud = (x,y+1)
                        if x == self.conf.xsize-1:
                            right = False
                        else:
                            right = occu[(u,ur),t].x == 1
                        if y == self.conf.ysize-1:
                            down = False
                        else:
                            down = occu[(u,ud),t].x == 1
                        if right and down:
                            s += '{:^3}'.format('+')
                        elif right:
                            s += '{:^3}'.format('_')
                        elif down:
                            s += '{:^3}'.format('|')
                        else:
                            s += '{:^3}'.format('.')

                    print(s)

                #check for nstat errors
                s = 0
                for v,w in itertools.product(self.conf.nodes(),what):
                    s += nstat[v,w,t].x
                print(s)

                #check for decisions errors
                s = 0
                for v in self.conf.nodes():
                    for d,w in itertools.product(diriter, moveWhat):
                        s += go[v,w,d,t].x
                        s += stop[v,w,d,t].x
                        s += cont[v,w,d,t].x
                    for w in liftWhat:
                        s += lift[v,w,t].x
                    for w in dropWhat:
                        s += drop[v,w,t].x
                print(s)
                sys.stdin.read(1)

        else:
            mo.computeIIS()
            mo.write("model.ilp")
