import huffman as huff
import random as rand
import sys

from math import log

CHARSIZE = 7

def entropy(freq):
    """ Calculate Entropy of a set of symbols and their frequencies """
    total = sum([f[1] for f in freq]) / 1.0
    return -sum([ f[1]/total * log(f[1]/total, 2) for f in freq ])

def mean_bits(freq, codes):
    """ Calculate mean bits used by a code table """
    total = sum([f[1] for f in freq]) / 1.0
    mbs = sum([f/total * len(codes[sym]) for sym, f in freq])
    return mbs


if __name__ == "__main__":
    # Table of frequencies, does not need to add up to 1 or 100 or some arbitrary
    # number. It can be interpreted as absolute symbol counts
    freq = [
        ('D', 30),
        ('K', 20),
        ('Q', 20),
        ('J', 15),
        ('10', 10),
        ('9', 5),
    ]
    

    # Easily create a text with the desired distribution by adding as many items
    # to an array as the frequency of the item
    freqtable = []
    for symbol, f in freq:
        freqtable += [symbol] * f

    text = ""

    # Add a random symbol from the freq table, over many iterations this converges
    # to the distribution given by the frequency table
    for i in range(50000):
        text += rand.choice(freqtable)

    # Generate the huffman tree and a corresponding translation table
    # for this 
    tree = huff.huffman_tree(freq)
    codes = huff.huffman_codes(tree)

    # Encode the text using the generated huffman codes
    encoded = huff.huffman_encode(text, codes)

    # Calcualte number of bits used by the plain text and the huffman encoded bits
    bits_text = len(text) * CHARSIZE * 1.0
    bits_encoded = len(encoded)

    print "text: ", text[:16], "..."
    print "encoded: ", encoded[:16], "..."
    print "compression: %.5f%%" % (bits_encoded / bits_text)

    # Entropy and mean bits per symbol:
    ent = entropy(freq)
    mbs = mean_bits(freq, codes)

    print "entropy  ", ent
    print "mean bits", mbs

    # Compression ratio:
    cr = CHARSIZE / mbs
    print "Huffman compression ratio %.2f:1" % cr