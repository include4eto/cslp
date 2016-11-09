#!/usr/bin/env python2.7
import numpy as np
from functools import reduce
from math import log
import sys

def inv_erlang_k(k, l):
	rand = np.random.uniform(low=0, high=1, size=(k, 1))
	prod = reduce(lambda x, y: x * y, rand)
	
	return -(1/l) * log(prod)

if __name__ == '__main__':
	num = sys.argv[1] if len(sys.argv) > 1 else 1
	num = int(num)

	for i in xrange(0, num):
		print(inv_erlang_k(10, 4))