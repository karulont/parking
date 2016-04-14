def normalizeEdge(edg):
    (x1,y1), (x2,y2) = edg
    if x2 > x1:
        return edg
    elif x1 == x2:
        if y1 < y2:
            return edg
        else:
            return (x2,y2),(x1,y1)
    else:
        return (x2,y2),(x1,y1)

def whatSE(w):
    if w == 'r':
        return ('e','r')
    elif w == 'cr':
        return ('e','cr')
    elif w == 'rc':
        return ('c','r')
    else:
        raise NameError(w)
