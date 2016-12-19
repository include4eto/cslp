from simulation.event_dispatcher import EventDispatcher
from simulation.simulation import Simulation
from output_formatter import OutputFormatter
from config import config as app_config
from statistics.statistics_aggregator import StatisticsAggregator
import itertools
import sys

import pprint

class ExperimentManager:
	"""Performs a run given a config file. Can run as many experiments as needed."""

	EXPERIMENT_HEADER = "Experiment #{0}: {1}"

	def __init__(self, config, disable_output=False, disable_statistics=False):
		self.config = config
		self.disable_output = disable_output
		self.disable_statistics = disable_statistics

		# make a grid of all experimentation configurations
		if len(config['experiments']):
			# convert to tuples so we can create the cartesian product
			experiments = []
			for k, values in config['experiments'].items():
				experiment = []

				# append to config for initialization purposes
				self.config[k] = values[0]

				for v in values:
					experiment.append({ 'key': k, 'value': v})
				experiments.append(experiment)

			# get the cartesian product
			self.grid = itertools.product(*experiments)
		else:
			self.grid = None

		# convert stop time to seconds
		self.stop_time = self.config['stopTime'] * 60 * 60
		self.stop_time = int(self.stop_time)		

		# create simulation and dispatcher objects
		# first create an event dispatcher
		self.dispatcher = EventDispatcher(self.stop_time, config['noAreas'])
		self.simulation = Simulation(self.config, self.dispatcher)
		self.output_formatter = OutputFormatter(self.dispatcher)
		self.statistics_aggregator = StatisticsAggregator(self.config, self.dispatcher)

		self.validation_errors = False
		# the simulation checks for valid configuration, see if there were any errors
		for i in (self.simulation.validate_errors + self.simulation.validate_warnings):
			print(i)
			
		if self.simulation.simulation_aborted:
			print('Configuration validation errors occurred. Exiting...\n')
			self.validation_errors = True

	def run_all(self):
		if self.validation_errors:
			return
		
		if self.grid is None:
			# this means no experiments, enable verbose output and run the one simulation
			self._run_experiment(self.config, enable_verbose = not self.disable_output)
		else:
			count = 1
			# run all experimentations
			for experiment in self.grid:
				description = ""
				for var in experiment:
					# print the description text
					self.config[var['key']] = var['value']
					description += ' {0} {1}'.format(var['key'], var['value'])
				
				experiment_text = ExperimentManager.EXPERIMENT_HEADER.format(
					count, description
				)
				if not self.disable_statistics:
					pass
					# print(experiment_text)
				
				count += 1
				# run the experiment
				self._run_experiment(self.config, enable_verbose = False)


	def _run_experiment(self, config, enable_verbose = False):
		# create the output formatter, if we need verbose output
		self.output_formatter.enabled = enable_verbose

		# reset everything and run
		self.dispatcher.reset()
		self.simulation.reset(config)
		self.statistics_aggregator.reset(config)
		self.simulation.run()

		while True:
			current_time = self.dispatcher.next_event()

			if current_time == False:
				# simulation end
				break
		
		# print statistics
		if not self.disable_statistics:
			self.statistics_aggregator.print_output()
