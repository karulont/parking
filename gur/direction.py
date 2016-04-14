WEST = 0
NORTH = 1
EAST = 2
SOUTH = 3

def dir2c(d):
    if d == WEST:
        return 'W'
    elif d == NORTH:
        return 'N'
    elif d == EAST:
        return 'E'
    elif d == SOUTH:
        return 'S'

def oppositeDir(d):
    return (d+2) % 4

diriter = range(4)
