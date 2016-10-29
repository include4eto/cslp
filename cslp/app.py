#!/usr/bin/env python3

import sys
from input_parser import *
from simulation.event_dispatcher import EventDispatcher
from simulation.simulation import Simulation
from output_formatter import OutputFormatter

# TODO: remove this
import pprint

def print_usage():
	print('Usage: TODO')

def start_simulation_run(config):
	# convert stop time to seconds
	stop_time = config['stopTime'] * 60 * 60
	stop_time = int(stop_time)

	# first create an event dispatcher
	dispatcher = EventDispatcher(stop_time, config['noAreas'])

	sim = Simulation(config, dispatcher)

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

	if not result:
		print('Parse errors occurred. Exiting...')
		for i in (parser.parse_errors + parser.parse_warnings):
			print(i)

		sys.exit(1)
	
	# start the simulation here
	start_simulation_run(parser.config)
	
	# print('Configuration read from {0}.'.format(file_path))
	# print('Exiting.')
	