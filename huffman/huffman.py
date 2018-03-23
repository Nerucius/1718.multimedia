""" Huffman Tree Encoder and Decoder """

from binarytree import (left as l, right as r, parent as p, trim)
from pqueue import top, insert, bot


def _huffman_descend(tree, root):
    """ Recursive descend a huffman tree, splitting tuple nodes into more leaves """

    # unpack item and freq
    (a, b), freq = tree[root]
    ai, af = a
    bi, bf = b

    # bigger freq -> left
    #  lower freq -> right
    if af > bf:
        tree[l(root)] = (ai,af)
        tree[r(root)] = (bi,bf)

        # If node is still a tuple, descend
        if type(a[0]) == tuple:
            _huffman_descend(tree, l(root))
        if type(b[0]) == tuple:
            _huffman_descend(tree, r(root))

    else:
        tree[l(root)] = (bi,bf)
        tree[r(root)] = (ai,af)

        # If node is still a tuple, descend
        if type(a[0]) == tuple:
            _huffman_descend(tree, r(root))
        if type(b[0]) == tuple:
            _huffman_descend(tree, l(root))


def huffman_tree(freq):
    """ Takes a list of (symbol, frequency) tuples and generates
    the corresponding huffman tree """
    
    # Data structures
    tree = [None] * (len(freq) ** 2)
    pq = []
    codes = {}

    # Don't assume frequencies will be sorted, insert into priority queue
    # instead of using freq array directly
    for item in freq:
        pq = insert(pq, item)

    # Group symbols from the botton of the priority queue
    while len(pq) > 1:
        # Last two items of the list
        z = bot(pq)
        y = bot(pq)

        # Join and insert into priority list, new priority is
        # sum of two prevs
        yz = ((y,z), y[1] + z[1])
        pq = insert(pq, yz)

    # Root node is all symbols, freq is 100%
    tree[0] = top(pq)

    # Recursive descent of the tree from the root node downwards
    _huffman_descend(tree, 0)      
    
    return trim(tree)


def _huffman_codes(tree, codes, root=0, currcode=""):
    """ Recursively descend tree, appending chars to codes as it goes down """

    if root > len(tree) or tree[root] == None:
        return

    item, freq = tree[root]

    if type(item) == tuple:
        _huffman_codes(tree, codes, l(root), currcode+"0")
        _huffman_codes(tree, codes, r(root), currcode+"1")
    else:
        codes[item] = currcode


def huffman_codes(tree):
    """ Retuns the binary codes for the given huffman tree's characters """

    codes = {}
    _huffman_codes(tree, codes)
    return codes


def _translate(text, table):
    """ Converts a continuous string to codes specified in a table """
    ptr = 0
    encoded = ""

    # Stop when we're past the strig
    while ptr < len(text):
        # end is how many bits ahead we look
        end = 1

        # Keep looking ahead while no match in reverse dict
        while text[ptr:ptr+end] not in table:
            end += 1

        # Add match to text
        symbol = text[ptr:ptr+end]
        encoded += table[symbol]
        # advance pointer as many steps as we looked ahead
        ptr += end

    return encoded


def huffman_encode(text, codes):
    return _translate(text, codes)


def huffman_decode(bits, codes):
    reverse = {v: k for k, v in codes.items()}
    return _translate(bits, reverse)


if __name__ == "__main__":
    # Test suite

    freq = [
        ('A', 250),
        ('B', 250),
        ('C', 140),
        ('D', 140),
        ('E', 55),
        ('F', 55),
        ('G', 55),
        ('H', 55),
    ]

    tree = huffman_tree(freq)
    codes = huffman_codes(tree)

    print codes

    text = "ABCDEFGH"
    encoded = huffman_encode(text, codes)
    bits_text = len(text) * 7.0
    bits_encoded = len(encoded) / 1.0

    print text
    print encoded
    print "compression: %.2f%%" %(bits_encoded / bits_text * 100)

    decoded = huffman_decode(encoded, codes)

    print "decoded again:", decoded
    print "is same?", text == decoded

