import numpy as np
from functools import reduce
from math import log

class DisposalModeling:
	@staticmethod
	def inv_erlang_k(k, l):
		rand = np.random.uniform(low=0, high=1, size=(k, 1))
		prod = reduce(lambda x, y: x * y, rand)
		
		return -(1/l) * log(prod)
