from tkinter import Tk, Canvas, mainloop, Label, Button, LEFT, RIGHT, HIDDEN, NORMAL
from direction import *
import itertools

class Visualize:
    def __init__(self, model):
        self.model = model
        self.time = 0

        self.shiftRight = 20
        self.shiftDown = 20
        self.separation = 90
        self.scale = 60
        self.textVShift = 10

        self.root = Tk()
        self.canvas = Canvas(self.root)
        self.canvas.pack()
        self.root.bind("<KeyRelease>", self.key_released)
        self.timeLabel = Label(self.root, text='time_lavel')
        self.timeLabel.pack(side=RIGHT)

        self.setup()
        self.draw()

        mainloop()

    def key_released(self, event):
        if event.char == 'j':
            if self.time < self.model.conf.maxt - 7:
                self.time = self.time + 1
                self.draw()
        elif event.char == 'k':
            if self.time > 0:
                self.time = self.time - 1
                self.draw()
        elif event.char == 'q':
            self.root.quit()

    def getBBox(self, v):
        return (self.shiftRight + self.separation*v[0],
                self.shiftDown + self.separation*v[1],
                self.shiftRight + self.separation*v[0] + self.scale,
                self.shiftDown + self.separation*v[1] + self.scale)

    def getCenter(self, v):
        return (self.shiftRight + self.separation*v[0] + self.scale / 2,
                self.shiftDown + self.separation*v[1] + self.scale / 2)

    def getStatusPos(self, v):
        (x,y) = self.getCenter(v)
        return (x,y - self.textVShift)

    def getDecisionPos(self, v):
        (x,y) = self.getCenter(v)
        return (x,y + self.textVShift)

    def getEdgePos(self, e):
        v0 = self.getCenter(e[0])
        v1 = self.getCenter(e[1])
        if v0[0] == v1[0]:
            if v0[1] < v1[1]:
                return (v0[0], v0[1] + self.scale / 2), (v1[0], v1[1] - self.scale / 2)
            else:
                return (v0[0], v0[1] - self.scale / 2), (v1[0], v1[1] + self.scale / 2)
        elif v0[1] == v1[1]:
            if v0[0] < v1[0]:
                return (v0[0] + self.scale / 2, v0[1]), (v1[0] - self.scale / 2, v1[1])
            else:
                return (v0[0] - self.scale / 2, v0[1]), (v1[0] + self.scale / 2, v1[1])
        return v0, v1

    def setup(self):
        self.nodeStatus = {}
        self.nodeDecision = {}
        for v in self.model.conf.nodes():
            self.canvas.create_oval(self.getBBox(v))
            self.nodeStatus[v] = self.canvas.create_text(self.getStatusPos(v), text="asfs")
            self.nodeDecision[v] = self.canvas.create_text(self.getDecisionPos(v), text="fs")
        self.edges = {}
        for e in self.model.conf.edges():
            self.edges[e] = self.canvas.create_line(self.getEdgePos(e), arrow='last')

    def draw(self):
        # quick reference
        nstat = self.model.vars.nstat
        occu = self.model.vars.occu
        go = self.model.vars.go
        stop = self.model.vars.stop
        cont = self.model.vars.cont
        lift = self.model.vars.lift
        drop = self.model.vars.drop

        what = self.model.conf.what
        moveWhat = self.model.conf.moveWhat
        liftWhat = self.model.conf.liftWhat
        dropWhat = self.model.conf.dropWhat
        conf=self.model.conf

        self.timeLabel.config(text = '%r' % self.time)
        t = self.time
        for v in self.model.conf.nodes():
            for w in what:
                if nstat[v,w,t].x == 1:
                    self.canvas.itemconfig(self.nodeStatus[v], text=w)
                    break

            decision = ''
            for d,w in itertools.product(diriter, moveWhat):
                if conf.checkNode(conf.edg(v,d)):
                    if go[v,w,d,t].x == 1:
                        decision = 'GO_{}{}'.format(d,w)
                    if stop[v,w,d,t].x == 1:
                        decision = 'STOP_{}{}'.format(d,w)
                    if cont[v,w,d,t].x == 1:
                        decision = 'CONT_{}{}'.format(d,w)
            for w in liftWhat:
                if lift[v,w,t].x == 1:
                    decision = 'LIFT_{}'.format(w)
            for w in dropWhat:
                if drop[v,w,t].x == 1:
                    decision = 'DROP_{}'.format(w)
            self.canvas.itemconfig(self.nodeDecision[v], text=decision)

        for e in self.model.conf.edges():
            state = HIDDEN
            if occu[e,t].x == 1:
                state = NORMAL

            self.canvas.itemconfig(self.edges[e], state=state)
