config = {
	'usage': """
Run a stochastic simulation of bin disposals in one or multiple areas given
simulation parameters. See the enclosed README.MD file for more details.

Algorithms:
	greedy - Select the bins with more garbage first
	priority - Select the closest bins first (userful for clusters or neighborhoods)
	dynamic - Select one of greedy | priority based on the number of bins.

Allowed configuration parameters are:
	lorryVolume - Total waste volume a lorry can accommodate (cubic metres) 
	lorryMaxLoad - Maximum lorry load (kg)
	binServiceTime - Time required to empty a bin (in seconds)
	binVolume - Bin volume (cubic metres)
	disposalDistrRate - Rate of the Erlang distribution of the 
			    disposal events (avg. no. per hour)
	disposalDistrShape - Shape of the Erlang distribution
	bagVolume - Bag volume (cubic metres)
	bagWeightMin - Minimum expected weight of a waste bag disposed
	bagWeightMax - Maximum expected weight
	noAreas - Number of service areas
	areaIdx <int> - area description
		serviceFreq <float>
		thresholdVal <float>
		noBins <int>
	roadsLayout - Road layout and distances between
		      bin locations (in minutes)
	stopTime - Simulation duration (hours)
	warmUpTime - Warm-up time (hours) allowed before collecting statistics
	"""
}

defaults = {
	'CACHE_SIZE': 30000000,
	'ALGORITHM': 'dynamic',
	'CACHE_STATE': True
}
