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
        self.model.params.Heuristics = 0.9
        self.model.params.Cuts = 0

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
        whats = self.conf.whats

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
        for u,w,d in itertools.product(self.conf.nodes(), whats.moveWhat, diriter):
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
            s = [nstat[v,w,t] for w in whats.what]
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
            if checkEdge((u,v)):
                s.append(occu[(u,v),t])
            e = (v,edg(v,dirPlus1[d]))
            if checkEdge(e):
                s.append(occu[e,t])
            e = (v,edg(v,dirMinus1[d]))
            if checkEdge(e):
                s.append(occu[e,t])
            mo.addConstr(quicksum(s) <= 1)

        # no more than one decision per node per timestep
        for v,t in itertools.product(nodes(), timeiter):
            s = []
            for d,w in itertools.product(diriter, whats.moveWhat):
                if checkNode(edg(v,d)):
                    s.append(go[v,w,d,t])
                    s.append(stop[v,w,d,t])
                    s.append(cont[v,w,d,t])
            for w in whats.liftWhat:
                s.append(lift[v,w,t])
            for w in whats.dropWhat:
                s.append(drop[v,w,t])
            mo.addConstr(quicksum(s) <= 1)

        # robot movements
        for u,w,d in itertools.product(nodes(), whats.moveWhat, diriter):
            v = edg(u,d);
            vp = edg(v,d);
            e = (u,v)
            if not checkNode(v):
                # Off grid in that direction
                continue
            for t in timeiter:
                mo.addConstr(go[u,w,d,t] - nstat[u,w,t] <= 0)

                if (d == 'N' or d == 'S') and (w in whats.dropWhat):
                    # movement is slow and length is long
                    td = 5
                elif (d == 'E' or d == 'W') and (w in whats.robotsWhat):
                    # movement fast and lenght short
                    td = 2
                else:
                    # movement fast and long or movement slow and short
                    td = 3

                if not checkTime(t,td):
                    # cannot complete
                    mo.addConstr(go[u,w,d,t] == 0)
                    continue
                td1 = td - 1
                td2 = 2 * td1

                # go implies stop or cont
                mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+td1] -cont[u,w,d,t+td1] +nstat[u,w,t] <= 1)

                # make sure edges are used
                for i in range(td+1):
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[e,t+i] <= 1)
                # make sure the node status remains same for duration of movement
                for i in range(1,td):
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

                # cont or stop add to 1
                mo.addConstr(stop[u,w,d,t] + cont[u,w,d,t] <= 1)
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
                    for i in range(self.conf.K):
                        vs.append('rsc' + str(i))
                        vs1.append('sc' + str(i))
                elif w in whats.liftWhat:
                    us = whats.removeRobotWhat[w]
                    vs = ['r', 'rc']
                    vs1 = ['e', 'c']
                    for i in range(self.conf.K):
                        vs.append('rsc' + str(i))
                        vs1.append('sc' + str(i))
                elif w in whats.dropWhat:
                    us = 'e'
                    vs = [w]
                    vs1 = ['e']
                else:
                    assert False, 'w = %r, liftWhat=%r' % (w, whats.liftWhat)

                # construct set of things, which could move at same time
                # TODO: look this over
                if w == 'r':
                    behind = whats.moveWhat
                    infront = whats.robotsWhat
                elif w in whats.liftWhat:
                    behind = whats.robotsWhat
                    infront = whats.robotsWhat
                elif w in whats.dropWhat:
                    behind = whats.dropWhat
                    infront = whats.moveWhat

                up = edg(u,oppositeDir(d))
                umore = []
                vmore = []
                if checkNode(up):
                    for ws in behind:
                        umore.append(cont[up,ws,d,t+td1])
                        umore.append(stop[up,ws,d,t+td1])
                if checkNode(vp):
                    for ws in infront:
                        vmore.append(cont[v,ws,d,t+td1])
                        vmore.append(stop[v,ws,d,t+td1])
                umore = quicksum(umore)
                vmore = quicksum(vmore)

                # (stop or cont) implies u status
                mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] - nstat[u,us,t+td] -umore <= 0)

                # more specific u status
                if checkNode(up):
                    for ws in behind:
                        usPlusWs = whats.usPlusWs[us][ws]
                        mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] -nstat[u,usPlusWs,t+td] 
                            +cont[up,ws,d,t+td1] +stop[up,ws,d,t+td1] <= 1)
                       # mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] +nstat[u,usPlusWs,t+td] 
                       #     -cont[up,ws,d,t+td1] -stop[up,ws,d,t+td1] <= 1)

                # (stop or cont) implies v status
                nst = []
                for s in vs:
                    nst.append(nstat[v,s,t+td])
                nst = quicksum(nst)
                mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] - nst <= 0, 'paks')

                # more specific v status
                for i in range(len(vs)):
                    mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] -nstat[v,vs1[i],t+td1]
                        +nstat[v,vs[i],t+td] -vmore <= 1, 'pikk')
                    mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] +nstat[v,vs1[i],t+td1]
                        -nstat[v,vs[i],t+td] -vmore <= 1, 'pakk')

        # general node status changes
        for u,w,t in itertools.product(nodes(), whats.what, timeiter):
            if not checkTime(t,1):
                continue

            more = []
            away = []

            (wi, wo) = whats.nodeStatusIO[w]
            if w in whats.liftWhat:
                away.append(lift[u,w,t])
            elif w in whats.dropWhat:
                away.append(drop[u,w,t])
            elif w in whats.allLiftWhat:
                if checkTime(t,-5):
                    for wl in whats.liftWhat:
                        more.append(lift[u,wl,t-5])
            elif w in whats.allDropWhat:
                if checkTime(t,-1):
                    for wd in whats.dropWhat:
                        more.append(drop[u,wd,t-1])

            for d,wt in itertools.product(diriter, wi):
                v = edg(u,d);
                if checkNode(v):
                    more.append(cont[v,wt,oppositeDir(d), t])
                    more.append(stop[v,wt,oppositeDir(d), t])
            for d,wt in itertools.product(diriter, wo):
                if checkNode(edg(u,d)):
                    away.append(stop[u,w,d,t]);
                    away.append(cont[u,w,d,t]);

            more = quicksum(more)
            away = quicksum(away)
            mo.addConstr(nstat[u,w,t] -nstat[u,w,t+1] -more -away <= 0)
            mo.addConstr(nstat[u,w,t] -nstat[u,w,t+1] +more +away <= 2)
            mo.addConstr(more <= 1)
            mo.addConstr(away <= 1)
            mo.addConstr(nstat[u,w,t+1] +more -away <= 1)

        # edge not in use constraints
        for u,d in itertools.product(nodes(), diriter):
            v = edg(u,d)
            if not checkNode(v):
                continue
            e = (u,v)
            if not checkEdge(e):
                continue

            for t in timeiter:
                # collect stuff
                incoming = []
                for w in whats.moveWhat:
                    if (d == 'N' or d == 'S') and (w in whats.dropWhat):
                        # movement is slow and length is long
                        td = 5
                    elif (d == 'E' or d == 'W') and (w in whats.robotsWhat):
                        # movement fast and lenght short
                        td = 2
                    else:
                        # movement fast and long or movement slow and short
                        td = 3
                    for tdd in range(td+1):
                        tc = t-tdd
                        if not checkTime(t, -tdd):
                            continue
                        incoming.append(go[u,w,d,tc])
                        incoming.append(stop[u,w,d,tc])
                        incoming.append(cont[u,w,d,tc])

                incoming = quicksum(incoming)
                mo.addConstr(occu[e,t] - incoming <= 0, 'asd')
                mo.addConstr( -2*occu[e,t] + incoming <= 0, 'asd2')



        # dropping constraints
        for v,w,t in itertools.product(nodes(), whats.dropWhat, timeiter):
            if checkTime(t,2):
                # drop implies correct start node status
                mo.addConstr(drop[v,w,t] -nstat[v,w,t] <= 0)
                # drop implies intermediate node status
                mo.addConstr(drop[v,w,t] -nstat[v,'drp',t+1] <= 0)
                ws = whats.dropWhatHelper[w]
                # drop implies end node status
                mo.addConstr(drop[v,w,t] -nstat[v,ws,t+2] <= 0)
            else:
                # cannot complete operation: disable it
                mo.addConstr(drop[v,w,t] == 0)

        # lifting constraints
        for v,w,t in itertools.product(nodes(), whats.liftWhat, timeiter):
            if checkTime(t,6):
                # lift implies correct start node status
                mo.addConstr(lift[v,w,t] -nstat[v,w,t] <= 0)
                # lift implies intermediate node status
                for i in range(1,6):
                    mo.addConstr(lift[v,w,t] -nstat[v,'lft',t+i] <= 0)
                ws = whats.dropWhatHelper[w]
                # lift implies end node status
                mo.addConstr(lift[v,w,t] -nstat[v,ws,t+6] <= 0)
            else:
                # cannot complete operation: disable it
                mo.addConstr(lift[v,w,t] == 0)

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

