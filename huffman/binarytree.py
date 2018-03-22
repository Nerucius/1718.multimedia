""" Functional Binary Tree """


def left(i):
    return 2*i + 1

def right(i):
    return 2*i + 2

def parent(i):
    return (i-1) // 2

def trim(tree):
    """ Trim a tree from both ends """

    min_idx = 0
    while tree[min_idx] == None:
        min_idx += 1

    max_idx = len(tree)-1

    while tree[max_idx] == None:
        max_idx -= 1

    return tree[min_idx:max_idx+1]