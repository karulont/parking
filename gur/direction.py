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

diriter = {'N','E','S','W'}
