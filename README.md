# 1718.multimedia

[Link to: Github Repository](https://github.com/Nerucius/1718.multimedia)

## Huffman Coding in Python

Implemented using an *Unbalanced Binary Tree* and a *Priority Queue*.  
Fundamentals for the binary tree taken from: [http://opendatastructures.org](http://opendatastructures.org/versions/edition-0.1d/ods-java/node52.html)

### How to run:

```
$ cd huffman
$ python main.py
```

**Example Output**

```
symbol bits:
	10 	0110
	D 	00
	K 	10
	J 	010
	Q 	11
	9 	0111
entropy   2.40869496956
mean bits 2.45
Huffman compression ratio 2.86:1
------------------------
text:  Q10DQ10KJQJDDKQJ ...
encoded:  1101100011011010 ...
text == decoded: True
size after compression: 0.31783%
NOTE: compression ratio afected by symbol '10' being 2 characters.
```

### Running the test suites:

```
$ cd huffman
$ python huffman.py
$ python pqueue.py
```