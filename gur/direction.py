def oppositeDir(d):
    if d == 'W':
        return 'E'
    elif d == 'N':
        return 'S'
    elif d == 'E':
        return 'W'
    elif d == 'S':
        return 'N'
    else:
        raise Error('Unknown dir')

dirPlus1 = {'N':'E', 'E':'S', 'S':'W', 'W':'N'}
dirMinus1 = {'N':'W', 'E':'N', 'S':'E', 'W':'S'}

diriter = {'N','E','S','W'}
