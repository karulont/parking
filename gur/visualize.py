from tkinter import Tk, Canvas, mainloop, Label, Button, LEFT, RIGHT, HIDDEN, NORMAL, BOTH, YES
from direction import *
import itertools

class Visualize:
    def __init__(self, solution):
        self.solution = solution
        self.time = 0

        self.shiftRight = 20
        self.shiftDown = 20
        self.separation = 90
        self.scale = 60
        self.textVShift = 10

        self.root = Tk()
        self.canvas = Canvas(self.root)
        self.canvas.pack(fill=BOTH, expand=YES)
        self.root.bind("<KeyRelease>", self.key_released)
        self.timeLabel = Label(self.root, text='time_lavel')
        self.timeLabel.pack(side=RIGHT)

        self.setup()
        self.draw()

        mainloop()

    def key_released(self, event):
        if event.char == 'j':
            if self.time < self.solution.maxt:
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
        for v in self.solution.nodes:
            self.canvas.create_oval(self.getBBox(v))
            self.nodeStatus[v] = self.canvas.create_text(self.getStatusPos(v), text="asfs")
            self.nodeDecision[v] = self.canvas.create_text(self.getDecisionPos(v), text="fs")
        self.edges = {}
        for e in self.solution.edges:
            self.canvas.create_line(self.getEdgePos(e), fill='gray')
            self.edges[e] = self.canvas.create_line(self.getEdgePos(e), arrow='last')

    def draw(self):
        # quick reference
        nstat = self.solution.nstat
        occu = self.solution.occu
        command = self.solution.command

        self.timeLabel.config(text = '%r' % self.time)
        t = self.time
        for v in self.solution.nodes:
            self.canvas.itemconfig(self.nodeStatus[v], text=nstat[v,self.time])
            self.canvas.itemconfig(self.nodeDecision[v], text=command[v,self.time])

        for e in self.solution.edges:
            state = HIDDEN
            if occu[e,t] == 1:
                state = NORMAL
            self.canvas.itemconfig(self.edges[e], state=state)
