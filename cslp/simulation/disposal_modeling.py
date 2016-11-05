import numpy as np
from functools import reduce
from math import log

class DisposalModeling:
	"""
		Models disposal events.
	"""

	@staticmethod
	def inv_erlang_k(k, l):
		"""
			Returns a disposal delay modeled by an Erlang-K
			distribution.
		"""

		rand = []
		for i in range(0, k):
			r = np.random.uniform(low=0, high=1)
			# do this to exclude 0 from the random pool
			while r == 0:
				r = np.random.uniform(low=0, high=1)
			
			rand.append(r)
		print(rand)

		# the product of all the randomly generated numbers
		prod = reduce(lambda x, y: x * y, rand)
		
		# multiply by the coefficient and take the log
		# to sample from the erlang-k distribution
		return -(1/l) * log(prod)
