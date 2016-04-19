from gurobipy import *
import itertools
import sys
from util import *

from vars import *

class GurobiModel:

    def __init__(self, conf):

        self.conf = conf
        self.model = Model("parking")
        self.model.params.LogToConsole = False

        def addFunc(set, setname, key):
            set[key] = self.model.addVar(vtype = GRB.BINARY,
                    name = setname + str(key).replace(" ",""))

        self.vars = Vars(conf, addFunc)
        self.model.update()
        self.addConstraints()

    def addConstraints(self):
        mo = self.model
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

        # edge can be used once per timestep
        for u in nodes():
            for v,t in itertools.product(neighbours(u), timeiter):
                o = occu[(u,v),t]
                no = occu[(v,u),t]
                mo.addConstr(quicksum([o,no]) <= 1)

        # more than one vehicle cannot arrive at same node
        for v,t in itertools.product(nodes(), timeiter):
            s = []
            for u in neighbours(v):
                s.append(occu[(u,v),t])
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
                if checkNode(edg(v,d)):
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
            e = (u,v)
            if not checkNode(v):
                # Off grid in that direction
                continue
            for t in timeiter:
                mo.addConstr(go[u,w,d,t] - nstat[u,w,t] <= 0)

                if (d == NORTH or d == SOUTH) and (w == 'cr' or w in scrj):
                    # movement is slow and length is long
                    td = 5
                elif (d == EAST or d == WEST) and (w == 'r' or w == 'rc' or w in rscj):
                    # movement fast and lenght short
                    td = 2
                else:
                    # movement fast and long or movement slow and short
                    td = 3

                if not checkTime(t,td):
                    continue
                td1 = td - 1
                td2 = 2 * td1

                # go implies stop or cont
                mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+td1] -cont[u,w,d,t+td1] +nstat[u,w,t] <= 1)

                # make sure edges are used
                for i in range(td+1):
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+i] <= 1)
                # make sure the node status remains same for duration of movement
                for i in range(1,td): # TODO: can try range(td1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+i] <= 1)

                # not sure why this, but okay for now
                # make sure that node status is the same for at stop and go time
                mo.addConstr(stop[u,w,d,t+td1] -nstat[u,w,t] <= 0)
                mo.addConstr(cont[u,w,d,t+td1] -nstat[u,w,t] <= 0)
                mo.addConstr(stop[u,w,d,t+td1] -nstat[u,w,t+td1] <= 0)
                mo.addConstr(cont[u,w,d,t+td1] -nstat[u,w,t+td1] <= 0)
                # better for the last section
                mo.addConstr(stop[u,w,d,t+td1] - go[u,w,d,t] <= 0)
                mo.addConstr(cont[u,w,d,t+td1] - go[u,w,d,t] <= 0)
                # (go or cont) implies (cont or stop)
                mo.addConstr(go[u,w,d,t] +cont[u,w,d,t] -cont[u,w,d,t+td1] -stop[u,w,d,t+td1] == 0)

                if not checkNode(vp):
                    # if at edge, disable cont
                    mo.addConstr(cont[u,w,d,td1] == 0)

                if t < td1:
                    # disable cont or stop because could not be given
                    mo.addConstr(cont[u,w,d,t] == 0)
                    mo.addConstr(stop[u,w,d,t] == 0)

                # status of v at t+td
                if w == 'r':
                    us = 'e'
                    vs = ['r', 'rc']
                    vs1 = ['e', 'c']
                elif w == 'rc':
                    us = 'c'
                    vs = ['r', 'rc']
                    vs1 = ['e', 'c']
                elif w == 'cr':
                    us = 'e'
                    vs = ['cr']
                    vs1 = ['e']
                else:
                    raise Error('special cars not implemented!')

                # (stop or cont) implies u status
                mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] - nstat[u,us,t+td] <= 0)

                # (stop or cont) implies v status
                nst = []
                for s in vs:
                    nst.append(nstat[v,s,t+td])
                nst = quicksum(nst)
                mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] - nst <= 0)

                # more specific v status
                for i in range(len(vs)):
                    mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] -nstat[v,vs1[i],t+td1]
                        +nstat[v,vs[i],t+td] <= 1)
                    mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] +nstat[v,vs1[i],t+td1]
                        -nstat[v,vs[i],t+td] <= 1)

        # general node status changes
        for u,w,t in itertools.product(nodes(), what, timeiter):
            if not checkTime(t,1):
                continue

            contOrStop = []
            gos = []

            if w == 'e':
                wi = ['r','rc','cr']
                wo = []
            elif w == 'c':
                wi = ['r', 'rc']
                wo = []
            elif w == 'r':
                wi = []
                wo = ['r']
            elif w == 'rc':
                wi = []
                wo = ['r']
                gos.append(lift[u,w,t])
            elif w == 'cr':
                wi = []
                wo = ['cr']
                gos.append(drop[u,w,t])
            elif w == 'lft':
                wi = []
                wo = []
                if checkTime(t,-5):
                    for wl in liftWhat:
                        contOrStop.append(lift[u,wl,t-5])
            elif w == 'drp':
                wi = []
                wo = []
                if checkTime(t,-1):
                    for wd in dropWhat:
                        contOrStop.append(drop[u,wd,t-1])

            for d,wt in itertools.product(diriter, wi):
                v = edg(u,d);
                if checkNode(v):
                    contOrStop.append(cont[v,wt,oppositeDir(d), t])
                    contOrStop.append(stop[v,wt,oppositeDir(d), t])
            for d,wt in itertools.product(diriter, wo):
                if checkNode(edg(u,d)):
                    gos.append(stop[u,w,d,t]);
                    gos.append(cont[u,w,d,t]);

            SCS0 = quicksum(contOrStop)
            SG0 = quicksum(gos)
            mo.addConstr(nstat[u,w,t] -nstat[u,w,t+1] -SCS0 -SG0 <= 0)
            mo.addConstr(nstat[u,w,t] -nstat[u,w,t+1] +SCS0 +SG0 <= 2)
            mo.addConstr(SCS0 <= 1)
            mo.addConstr(SG0 <= 1)
            mo.addConstr(nstat[u,w,t+1] +SCS0 -SG0 <= 1)


        # dropping constraints
        for v,w,t in itertools.product(nodes(), dropWhat, timeiter):
            if checkTime(t,2):
                # drop implies correct start node status
                mo.addConstr(drop[v,w,t] -nstat[v,w,t] <= 0)
                # drop implies intermediate node status
                mo.addConstr(drop[v,w,t] -nstat[v,'drp',t+1] <= 0)
                if w == 'cr':
                    ws = 'rc'
                else:
                    raise Error('implement special')
                # drop implies end node status
                mo.addConstr(drop[v,w,t] -nstat[v,ws,t+2] <= 0)

        # lifting constraints
        for v,w,t in itertools.product(nodes(), liftWhat, timeiter):
            if checkTime(t,6):
                # lift implies correct start node status
                mo.addConstr(lift[v,w,t] -nstat[v,w,t] <= 0)
                # lift implies intermediate node status
                for i in range(1,6):
                    mo.addConstr(lift[v,w,t] -nstat[v,'lft',t+i] <= 0)
                if w == 'rc':
                    ws = 'cr'
                else:
                    raise Error('implement special')
                # lift implies end node status
                mo.addConstr(lift[v,w,t] -nstat[v,ws,t+6] <= 0)

        mo.update()


    def optimize(self):
        self.model.optimize()

    def setSituation(self, sit):
        sit.situation(self.model, self.vars)
        sit.objective(self.model, self.vars)
        self.model.update()

    def checkStatus(self):
        return self.model.status == GRB.status.OPTIMAL

    def findIIS(self, fname):
        self.model.computeIIS()
        self.model.write(fname + '.ilp')

