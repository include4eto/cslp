# Generates a valid big area to test
#	the performance of the simulation

import random
import sys

no_bins = 50

for y in range(no_bins):
	r = []
	for x in range(no_bins):
		if x == y:
			sys.stdout.write(' 0')
		else:
			path_len = 10
			sys.stdout.write(' {0}'.format(path_len))
	sys.stdout.write('\n')
		
sys.stdout.flush()
