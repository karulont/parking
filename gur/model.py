from gurobipy import *
import itertools
import sys

from vars import *

class GurobiModel:

    def __init__(self, conf, log=False):

        self.conf = conf
        self.model = Model("parking")
        self.model.params.LogToConsole = log
        self.model.params.Threads = 4
        self.model.params.Cuts = 0
        self.model.params.PrePasses = 3
        self.model.params.Presolve = 2
        self.model.params.Heuristics = 0
        self.model.params.MIPFocus = 2

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

        nodes = self.conf.nodes
        edges = self.conf.edges
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
        for u,w,d in itertools.product(self.conf.nodes(), whats.mcWhat, diriter):
            v = edg(u,d);
            if not self.conf.checkEdge((u,v)):
                # Off grid in that direction
                continue
            mo.addConstr(cont[u,w,d,0] == 0);
            mo.addConstr(stop[u,w,d,0] == 0);

        # some ideas for good constraints:
        #  * count the number of cars, make sure that it stays same
        #  * count the number of robots, make sure that it stays same
        # robotWhat = whats.moveWhat.union(whats.allLiftWhat, whats.allDropWhat)
        # for t in timeiter:
        #     for ti in range(t,self.conf.maxt+1):
        #         robotsnow = set()
        #         robotsnext = set()
        #         for v,w in itertools.product(nodes(), robotWhat):
        #             robotsnow.add(nstat[v,w,t])
        #             robotsnext.add(nstat[v,w,ti])
        #         mo.addConstr(quicksum(robotsnow) == quicksum(robotsnext), 'countR')

        # one status per node per timestep
        for v,t in itertools.product(nodes(), timeiter):
            s = [nstat[v,w,t] for w in whats.what]
            mo.addConstr(quicksum(s) == 1)

        # edge can be used once per timestep
        for u,v in edges():
            for t in timeiter:
                o = occu[(u,v),t]
                no = occu[(v,u),t]
                mo.addConstr(quicksum([o,no]) <= 1)

        # more than one vehicle cannot arrive at same node
        for v,t in itertools.product(nodes(), timeiter):
            s = []
            for u in neighbours(v):
                if checkEdge((u,v)):
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
            for d,w in itertools.product(diriter, whats.mcWhat):
                if checkEdge((v,edg(v,d))):
                    s.append(go[v,w,d,t])
                    s.append(stop[v,w,d,t])
                    s.append(cont[v,w,d,t])
            for w in whats.liftWhat:
                s.append(lift[v,w,t])
            for w in whats.dropWhat:
                s.append(drop[v,w,t])
            mo.addConstr(quicksum(s) <= 1)

        # robot movements
        for u,w,d in itertools.product(nodes(), whats.mcWhat, diriter):
            v = edg(u,d);
            vp = edg(v,d);
            e = (u,v)
            up = edg(u,oppositeDir(d))
            uWhat = {mw for mw in whats.moveWhat if whats.getMovingComponent[mw] == w}
            if not checkEdge(e):
                # Off grid in that direction
                continue
            for t in timeiter:
                uWhatsNow = {nstat[u,wp,t] for wp in uWhat}
                # go can be 1, when status is right
                mo.addConstr(go[u,w,d,t] -quicksum(uWhatsNow) <= 0, 'si')

                td = getMovementTime(d,w)
                td1 = td - 1

                if not checkTime(t,td1):
                    mo.addConstr(go[u,w,d,t] == 0)
                    continue

                goOrCont = {go[u,w,d,t]}
                if checkEdge((up,u)):
                    goOrCont.add(cont[up,w,d,t])
                    # go or cont sum to 1
                    mo.addConstr(quicksum(goOrCont) <= 1)

                goOrCont = quicksum(goOrCont)

                # go or cont implies stop or cont
                mo.addConstr(goOrCont -stop[u,w,d,t+td1] -cont[u,w,d,t+td1] == 0)

                if not checkTime(t,td):
                    # cannot complete
                    mo.addConstr(go[u,w,d,t] == 0)
                    continue

                # make sure edges are used
                for i in range(td):
                    mo.addConstr(goOrCont -occu[e,t+i] <= 0)
                # make sure the node status remains same for duration of movement
                for i,uw in itertools.product(range(1,td),uWhat):
                    mo.addConstr(goOrCont +nstat[u,uw,t] -nstat[u,uw,t+i] <= 1)

                # cont or stop sum to 1
                mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] <= 1)

                if not checkEdge((v,vp)):
                    # disable cont, because cannot go futher
                    mo.addConstr(cont[u,w,d,t+td1] == 0)

                if t < td1:
                    # disable cont or stop because could not be given
                    mo.addConstr(cont[u,w,d,t] == 0)
                    mo.addConstr(stop[u,w,d,t] == 0)

                # construct set of things, which could move at same time
                if w == 'r':
                    behind = whats.mcWhat
                    ahead = {'r'}
                else:
                    behind = whats.dropWhat
                    ahead = whats.mcWhat

                umore = []
                vless = []
                if checkEdge((up,u)):
                    for ws in behind:
                        umore.append(cont[up,ws,d,t+td1])
                        umore.append(stop[up,ws,d,t+td1])
                if checkEdge((v,vp)):
                    for ws in ahead:
                        vless.append(cont[v,ws,d,t+td1])
                        vless.append(stop[v,ws,d,t+td1])
                umore = quicksum(umore)
                vless = quicksum(vless)

                # (stop or cont) implies u status
                uless = {nstat[u,whats.removeMovingComponent[uw],t+td] for uw in uWhat}
                uless = quicksum(uless)
                mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] -uless -umore <= 0,'un')

                # more specific u status

                for uw in uWhat:
                    uLeft = whats.removeMovingComponent[uw]
                    mo.addConstr(
                            stop[u,w,d,t+td1] + cont[u,w,d,t+td1]
                            -umore
                            +nstat[u,uw,t+td1]
                            -nstat[u,uLeft,t+td] <= 1, 'afg')
                    if checkEdge((up,u)):
                        for ws in behind:
                            if ws in whats.addMovingComponent[uLeft]:
                                mo.addConstr(
                                        cont[up,ws,d,t+td1] +stop[up,ws,d,t+td1]
                                        +nstat[u,uw,t+td1]
                                        -nstat[u,whats.addMovingComponent[uLeft][ws],t+td]
                                        <= 1, '23')

                nst = {nstat[v,wu,t+td] for wu in uWhat}
                nst = quicksum(nst)
                # stop or cont implies v status
                mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] - nst <= 0, 'paks')
                for wv in uWhat:
                    vBefore = whats.removeMovingComponent[wv]
                    mo.addConstr(stop[u,w,d,t+td1] + cont[u,w,d,t+td1] -nstat[v,vBefore,t+td1]
                        +nstat[v,wv,t+td] -vless <= 1, 'pikk')


        # general node status changes
        for u,w,t in itertools.product(nodes(), whats.what, timeiter):
            if not checkTime(t,1):
                continue

            more = set()
            away = set()

            (wi, wo) = whats.nodeStatusIO[w]
            if w in whats.liftWhat:
                away.add(lift[u,w,t])
            elif w in whats.dropWhat:
                away.add(drop[u,w,t])
            elif w == 'lft' and checkTime(t,-5):
                for wl in whats.liftWhat:
                    more.add(lift[u,wl,t-5])
            elif w == 'drp' and checkTime(t,-1):
                for wd in whats.dropWhat:
                    more.add(drop[u,wd,t-1])

            for d,wt in itertools.product(diriter, wi):
                v = edg(u,d);
                if checkEdge((v,u)):
                    wtt = whats.getMovingComponent[wt]
                    more.add(cont[v,wtt,oppositeDir(d), t])
                    more.add(stop[v,wtt,oppositeDir(d), t])
            for d,wt in itertools.product(diriter, wo):
                if checkEdge((u,edg(u,d))):
                    wtt = whats.getMovingComponent[wt]
                    away.add(stop[u,wtt,d,t]);
                    away.add(cont[u,wtt,d,t]);

            more = quicksum(more)
            away = quicksum(away)
            mo.addConstr(nstat[u,w,t] -nstat[u,w,t+1] -more -away <= 0)
            mo.addConstr(nstat[u,w,t] -nstat[u,w,t+1] +more +away <= 2)
            mo.addConstr(more <= 1)
            mo.addConstr(away <= 1)
            mo.addConstr(nstat[u,w,t+1] +more -away <= 1)

        # edge not in use constraints
        for e,t in itertools.product(edges(), timeiter):
            u,v = e
            d = getEdgeDir(e)

            # collect stuff
            incoming = []
            for w in whats.mcWhat:
                td = getMovementTime(d,w)
                for tdd in range(td):
                    tc = t+tdd
                    if not checkTime(t, tdd):
                        continue
                    incoming.append(stop[u,w,d,tc])
                    incoming.append(cont[u,w,d,tc])

            incoming = quicksum(incoming)
            mo.addConstr(incoming <= 2, 'incoming')
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

    def writeToFile(self, file):
        self.model.write(file + '.lp.bz2')

    def setSituation(self, sit):
        sit.situation(self.model, self.vars)
        sit.objective(self.model, self.vars)
        self.model.update()

    def checkStatus(self):
        return self.model.status != GRB.status.INFEASIBLE

    def findIIS(self, fname):
        self.model.computeIIS()
        self.model.write(fname + '.ilp')

