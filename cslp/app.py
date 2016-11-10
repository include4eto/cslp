#!/usr/bin/env python2.7

import sys
from input_parser import *
from simulation.event_dispatcher import EventDispatcher
from simulation.simulation import Simulation
from output_formatter import OutputFormatter
from config import config as app_config

def print_usage():
	print(app_config['usage'])

def start_simulation_run(config):
	if len(config['experiments']):
		# print('Warning: Experiment detected. Experiments are not yet fully supported. Only the first value of the experiment will be used.')
		# polyfill/monkey patch to make experiments work for now
		# 	NOTE: this will disappear in the future, it makes the application work as is now
		for k, v in config['experiments'].items():
			config[k] = v[0]


	# convert stop time to seconds
	stop_time = config['stopTime'] * 60 * 60
	stop_time = int(stop_time)

	# first create an event dispatcher
	dispatcher = EventDispatcher(stop_time, config['noAreas'])

	sim = Simulation(config, dispatcher)
	# the simulation checks for valid configuration, see if there were any errors
	for i in (sim.validate_errors + sim.validate_warnings):
		print(i)
	if sim.simulation_aborted:
		print('Configuration validation errors occurred. Exiting...\n')
		sys.exit(1)
		return
	

	# create the output formatter
	output_formatter = OutputFormatter(dispatcher)
	sim.run()

	while True:
		current_time = dispatcher.next_event()

		if current_time == False:
			# simulation end
			break

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
		sys.exit(1)
	
	# start the simulation here
	start_simulation_run(parser.config)
