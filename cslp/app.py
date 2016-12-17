#!/usr/bin/env python2.7

import sys
from input_parser import *
from config import config as app_config
from experiment import Experiment
from timeit import default_timer as timer

def print_usage():
	print(app_config['usage'])

def start_simulation_run(config):
	"""
		Start the pipeline for the simulation. To be moved
		into a more specialized Experiment class when those are supported.
	"""
	
	experiment = Experiment(config)
	experiment.run_all()

def run_experiments(config):
	pass

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print_usage()
		sys.exit(0)
	
	file_path = sys.argv[1]
	 
	# create the parser
	parser = InputParser(file_path)
	result = parser.parse()

	for i in (parser.parse_errors + parser.parse_warnings):
		print(i)

	if not result:
		print('Parse errors occurred. Exiting...\n')
		sys.exit(0)
	
	# start the simulation here
	start_simulation_run(parser.config)
