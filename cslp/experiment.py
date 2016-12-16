from simulation.event_dispatcher import EventDispatcher
from simulation.simulation import Simulation
from output_formatter import OutputFormatter
from config import config as app_config
from statistics.statistics_aggregator import StatisticsAggregator
import itertools
import sys

import pprint

class Experiment:
	EXPERIMENT_HEADER = "Experiment #{0}: {1}"

	def __init__(self, config):
		self.config = config

		# make a grid of all experimentation configurations
		if len(config['experiments']):
			# convert to tuples so we can create the cartesian product
			experiments = []
			for k, values in config['experiments'].items():
				experiment = []
				for v in values:
					experiment.append({ 'key': k, 'value': v})
				experiments.append(experiment)

			# get the cartesian product
			self.grid = itertools.product(*experiments)
		else:
			self.grid = None

	def run_all(self):
		if self.grid is None:
			# this means no experiments, enable verbose output and run the one simulation
			self._run_experiment(self.config, enable_verbose = True)
		else:
			count = 1
			# run all experimentations
			for experiment in self.grid:
				description = ""
				for var in experiment:
					self.config[var['key']] = var['value']
					description += ' {0} {1}'.format(var['key'], var['value'])
				
				experiment_text = Experiment.EXPERIMENT_HEADER.format(
					count, description
				)
				print(experiment_text)
				count += 1
				# run the experiment
				self._run_experiment(self.config, enable_verbose = False)


	def _run_experiment(self, config, enable_verbose = False):

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
			sys.exit(0)
			return
		

		# create the output formatter, if we need verbose output
		if enable_verbose:
			output_formatter = OutputFormatter(dispatcher)
		
		statistics_aggregator = StatisticsAggregator(config, dispatcher)
		sim.run()

		while True:
			current_time = dispatcher.next_event()

			if current_time == False:
				# simulation end
				break
		statistics_aggregator.print_output()
