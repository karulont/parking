import itertools
from direction import *
from nodestatus import *
from gridconfig import GridConfig

class GridConfig_json(GridConfig):
    def __init__(self, jsondata, maxt):
        self.grid = jsondata[2]
        GridConfig.__init__(self, jsondata[1], jsondata[0], maxt, 3)

    def nodes(self):
        for y in range(self.ysize):
            for x in range(self.xsize):
                if self.grid[y][x] != '':
                    yield (x,y)

    def edges(self):
        for x,y in self.nodes():
            for d in self.grid[y][x]:
                yield (  (x,y),  edg((x,y),d)  )
