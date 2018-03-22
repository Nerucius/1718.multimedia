""" Functional Priority Queue """


def insert(queue, item):
    if len(queue) == 0:
        return [item]

    idx = 0
    while idx < len(queue) and queue[idx][1] > item[1]:
        idx += 1

    return queue[:idx] + [item] + queue[idx:]

def top(queue):
    item = queue[0]
    del queue[0]
    return item

def bot(queue):
    item = queue[-1]
    del queue[-1]
    return item


if __name__ == "__main__":
    """ test suite """
    
    queue = []
    queue = insert(queue, ('EMPTY', 1))
    print queue

    queue = [
        ('D', 30),
        ('K', 20),
        ('Q', 20),
        ('J', 15),
        ('10', 10),
        ('9', 5),
    ]

    queue = insert(queue, ('FIRST', 200))
    queue = insert(queue, ('MIDDLE', 19))
    queue = insert(queue, ('LAST', 0))

    print queue
