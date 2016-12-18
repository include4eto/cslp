#!/usr/bin/env python2.7

import sys
import argparse
from input_parser import *
from config import config as app_config
from config import defaults as app_defaults

from experiment_manager import ExperimentManager
from timeit import default_timer as timer
from simulation.route_planning.dijkstra_route_planner import DijkstraRoutePlanner


def start_simulation_run(config, disable_output):
	"""
		Start the pipeline for the simulation.
	"""
	
	# create the experiment with the specified configuration.
	#	It handles the rest.
	experiment_manager = ExperimentManager(config, disable_output=disable_output)
	if experiment_manager.validation_errors:
		return
	experiment_manager.run_all()

def run_experiments(config):
	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='CSLP', epilog=app_config['usage'], formatter_class=argparse.RawTextHelpFormatter)
	# add all arguments to the parser
	
	# this is the default behavior - only a file name and nothing else
	parser.add_argument('file_name', help='The input configuration file')

	# used to select the algorithm - greedy/priority/dynamic
	parser.add_argument('-a', '--algorithm',
		help='The algorithm to use.',
		type=str,
		choices=['greedy', 'priority', 'dynamic'],
		default=app_defaults['ALGORITHM']
	)

	# cache control
	parser.add_argument('-dc', '--disable-cache',
		help='Disable the algorithm route caching',
		action = 'store_true' if app_defaults['CACHE_STATE'] else 'store_false'
	)
	
	# cache size
	parser.add_argument('-cs', '--cache-size',
		help='Set the algorithm\'s cache size',
		default=app_defaults['CACHE_SIZE'],
		type=int
	)

	# time benchmark (useful for external statistics)
	parser.add_argument('-b', '--benchmark',
		help='Benchmark the algorithm\s run time',
		action='store_true'
	)

	# disables output even if only one experiment is run,
	#	useful to benchmark so it doesn't clutter your console
	parser.add_argument('-d', '--disable-output',
		help='Disable everything except statistics',
		action='store_true'
	)
	
	parser.add_argument('-dt', '--dynamic-threshold',
		help='Dynamic algorithm threshold',
		type=int,
		default=app_defaults['DYNAMIC_THRESHOLD']
	)

	args = parser.parse_args()

	file_path = args.file_name

	# set algorithm options
	DijkstraRoutePlanner.ALGORITHM = args.algorithm
	DijkstraRoutePlanner.CACHE_ENABLED = not args.disable_cache
	DijkstraRoutePlanner.CACHE_MAX_SIZE = args.cache_size
	DijkstraRoutePlanner.DYNAMIC_BINS_THRESHOLD = args.dynamic_threshold

	# create the parser
	parser = InputParser(file_path)
	result = parser.parse()

	# print errors, if any
	for i in (parser.parse_errors + parser.parse_warnings):
		print(i)

	if not result:
		print('Parse errors occurred. Exiting...\n')
		sys.exit(0)
	

	if args.benchmark:
		start_time = timer()

	# start the simulation here
	try:
		if args.disable_output:
			print('Detailed output disabled by user')
		start_simulation_run(parser.config, args.disable_output)
	except KeyboardInterrupt:
		print('\nApplication terminated by user.')

	if args.benchmark:
		# benchmark running time
		end_time = timer()
		runtime = end_time - start_time

		print('Total application runtime: {0} seconds'.format(runtime))
