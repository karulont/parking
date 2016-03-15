from gurobipy import *
import itertools
import sys
from stuff import *
from consts import *

def createModel():

    nstat = {}
    occu = {}
    mo = Model("parking")

    def addVar(set, setname, key):
        set[key] = mo.addVar(vtype = GRB.BINARY, name = setname + str(key).replace(" ",""))

    for (x,y),t in itertools.product(nodes(), timeiter):
        if x > 0:
            addVar(occu, "occu", ((x,y),(x-1,y),t))
        if y > 0:
            addVar(occu, "occu", ((x,y),(x,y-1),t))
        if x < xsize - 1:
            addVar(occu, "occu", ((x,y),(x+1,y),t))
        if y < ysize - 1:
            addVar(occu, "occu", ((x,y),(x,y+1),t))
        for w in what:
            addVar(nstat, "nstat", ((x,y), w, t))

    # add "decision" variables
    go = {}
    stop = {}
    cont = {}
    lift = {}
    drop = {}

    for v in nodes():
        for w,d,t in itertools.product(moveWhat, diriter, timeiter):
           addVar(go, "go", (v,w,d,t))
           addVar(stop, "stop", (v,w,d,t))
           addVar(cont, "cont", (v,w,d,t))
        for w,t in itertools.product(liftWhat, timeiter):
            addVar(lift, "lift", (v,w,t))
        for w,t in itertools.product(dropWhat, timeiter):
            addVar(drop, "drop", (v,w,t))

    mo.update()

    def checkNode(node):
        return (node,'e',0) in nstat

    def checkEdge(edge):
        return (edge, 0) in occu

    def checkTime(t, dt):
        return t+dt < maxt

    # add objective
    costvars = set()
    
    v = (0,0) # node where to dropoff cars
    for w,t in itertools.product(scj, timeiter):
        #costvars.add(nstat[v,w,t])
        pass
    # drop car TODO: temporary
    for t in timeiter:
        costvars.add(nstat[v,'rc',t])
    for var in costvars:
        var.obj = -1

    mo.update()
    print('Adding constraints')
    def fixInitialConfiguration():
        # initial configuration
        definedNodes = set()
        def specifyNode(x,y):
            nonlocal definedNodes
            v = (x,y)
            assert v not in definedNodes
            definedNodes.add(v)
            return v

        # important: at time 0 everything is still so do not allow continue or stop
        for u,w,d in itertools.product(nodes(), moveWhat, diriter):
            v = edg(u,d);
            if not checkNode(v):
                # Off grid in that direction
                continue
            mo.addConstr(cont[u,w,d,0] == 0);
            mo.addConstr(stop[u,w,d,0] == 0);


        # robot
        mo.addConstr(nstat[specifyNode(0,0), 'c', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'r', 0] == 1)
        mo.addConstr(nstat[specifyNode(1,1), 'e', 0] == 1)
        #mo.addConstr(drop[(0,0), 'cr', 0] == 1)
        """
        # special cars
        mo.addConstr(nstat[specifyNode(2,2), 'sc0', 0] == 1)
        mo.addConstr(nstat[specifyNode(3,3), 'sc1', 0] == 1)
        # empty places
        mo.addConstr(nstat[specifyNode(2,1), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(2,0), 'e', 0] == 1)
        mo.addConstr(nstat[specifyNode(0,1), 'e', 0] == 1)
        # all other nodes filled with anonymous cars
        for v in set(nodes()).difference(definedNodes):
            mo.addConstr(nstat[v, 'c', 0] == 1)
        """

    fixInitialConfiguration()

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
            o = occu[u,v,t]
            no = occu[v,u,t]
            mo.addConstr(quicksum([o,no]) <= 1)

    # more than one vehicle cannot arrive at same node
    for v,t in itertools.product(nodes(), timeiter):
        s = []
        for u in neighbours(v):
            s.append(occu[u,v,t])
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
        if not checkNode(v):
            # Off grid in that direction
            continue
        for t in timeiter:
            if (d == NORTH or d == SOUTH) and (w == 'cr' or w in scrj):
                # movement is slow and length is long
                if checkTime(t,5):
                    mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+4] -cont[u,w,d,t+4] +nstat[u,w,t] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+1] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+2] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+3] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+4] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,w,t+5] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[u,v,t+1] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[u,v,t+2] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[u,v,t+3] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[u,v,t+4] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,'e',t] <= 1)
            elif (d == EAST or d == WEST) and (w == 'r' or w == 'rc' or w in rscj):
                # movement fast and lenght short
                if checkTime(t,2):
                    mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+1] -cont[u,w,d,t+1] +nstat[u,w,t] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+1] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,w,t+2] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[u,v,t+1] <= 1)
            else:
                # movement fast and long or movement slow and short
                if checkTime(t,3):
                    mo.addConstr(go[u,w,d,t] -stop[u,w,d,t+2] -cont[u,w,d,t+2] +nstat[u,w,t] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+1] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[u,w,t+2] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -nstat[v,w,t+3] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[u,v,t+1] <= 1)
                    mo.addConstr(go[u,w,d,t] +nstat[u,w,t] -occu[u,v,t+2] <= 1)

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
                    gos.append(go[u,w,d,t]);

            SCS0 = quicksum(contOrStop)
            SG0 = quicksum(gos)
            mo.addConstr(nstat[u,'e',t] -nstat[u,'e',t+1] -SCS0 +SG0 == 0)

            mo.addConstr(-nstat[u,'e',t+1] -SCS0 +SG0 <= 0)
            mo.addConstr(-nstat[u,'e',t+1] <= 0)
            mo.addConstr(-SCS0 <= 0)
            mo.addConstr(-SG0 <= 0)
            mo.addConstr(nstat[u,'e',t+1] +SCS0 <= 1)


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

    mo.optimize()


    if mo.status == GRB.status.OPTIMAL:
        #print the solution
        for t in timeiter:
            print("timestep {0}:".format(t))
            for y in range(ysize):
                s = ''
                for x in range(xsize):
                    for w in what:
                        if nstat[(x,y),w,t].x == 1:
                            s += '{:^5}'.format(w)
                            break
                s += '\t\t'
                for x in range(xsize):
                    v = (x,y)
                    decision = '{:10}'.format('_')
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
                print(s)

            #check for nstat errors
            s = 0
            for v,w in itertools.product(nodes(),what):
                s += nstat[v,w,t].x
            print(s)

            #check for decisions errors
            s = 0
            for v in nodes():
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
                    
    # return the model
    return mo

def main():
    m = createModel()

if __name__ == '__main__':
    main()
