from .area import Area
from copy import deepcopy
from route_planning.dijkstra_route_planner import DijkstraRoutePlanner

import pprint
class Simulation:
	LORRY_CAPACITY_WARNING = "Validation Warning: Lorry capacity is too small. Lorry might not be able to fit in a full bin."
	LORRY_WEIGHT_ERROR = "Validation Error: Minimum bag weight is greater than lorry volume."
	BIN_WEIGHT_WARNING = "Validation Warning: Maximum bin weight might be larger than lorry maximum load."
	BIN_WEIGHT_LORRY_WARNING = "Validation Warning: Lorry might not be able to fill its maximum volume due to weight constraints"
	STATISTICS_WARNING = "Validation Warning: Warm up time is greater than stop time. No statistics will be reported."
	DISPOSAL_FREQUENCY_WARNING = "Validation Warning (Area {0}): Disposal rate is greater than service rate. This might be a mistake."
	BAG_WEIGHT_MIN_MAX_ERROR = "Validation Error: Mimimum bag weight is greater than maximum bag weight."
	DUPLICATE_AREA_INDEX = "Validation Error: Duplicate area index {0}"
	INVALID_AREA_INDEX = "Validation Error: Invalid area index {0}"
	MISSING_AREAS = "Validation Errors: Some areas are missing."
	BAD_THRESHOLD_VAL = "Validation Errors: Bad threshold value for area {0}"

	"""
		Simulation class. Combines many area classes
		and runs the simulation. Essentially a wrapper for the simulation.
	"""
	def __init__(self, config, event_dispatcher):
		# the init method will check the config for runtime inconsistencies,
		#	such as area indices being non-sequential (i.e. skipping one, etc.)
		# These we treat as configuration errors, rather than parse errors, since
		# 	that's what they are. The parser should have no notion of the Simulation
		#	and it doesn't. It only checks for syntax.
		self.config = config

		# this is injected at runtime through the constructor
		self.event_dispatcher = event_dispatcher

		self.validate_warnings = []
		self.validate_errors = []

		# sanity check inputs
		result = self._sanity_check(config)
		self.simulation_aborted = False
		if result == False:
			# stop the simulation in case of validation errors
			self.simulation_aborted = True
			return

		self.areas = []

		for i in xrange(0, self.config['noAreas']):
			# instantiate all areas with their respective configurations
			area_config = deepcopy(self.config)

			# copy area-specific properties to its config
			for key, val in area_config['areas'][i].items():
				if key not in area_config:
					area_config[key] = val

			# remove the overall configuration
			del area_config['areas']

			# select only the roads layout that the are needs
			self.areas.append(Area(area_config, event_dispatcher, DijkstraRoutePlanner))

	def _sanity_check(self, config):
		"""
			Does sanity checking on the configuration
		"""

		if config['lorryVolume'] * 2 < config['binVolume']:
			# we can't collect an overflowed bin
			# NOTE: The lorry compresses the contents of a bin
			self.validate_warnings.append(Simulation.LORRY_CAPACITY_WARNING)
		
		if config['bagWeightMin'] > config['lorryMaxLoad']:
			# we can't even collect one bag
			self.validate_errors.append(Simulation.LORRY_WEIGHT_ERROR)
			return False

		if config['bagWeightMin'] > config['bagWeightMax']:
			self.validate_errors.append(Simulation.BAG_WEIGHT_MIN_MAX_ERROR)
			return False
		
		if (config['binVolume'] / config['bagVolume']) * config['bagWeightMin'] > \
			config['lorryMaxLoad']:
			# again, we might not be able to collect an overflowed bin
			self.validate_warnings.append(Simulation.BIN_WEIGHT_WARNING)
		
		if ((2 * config['lorryVolume']) / config['bagVolume']) * config['bagWeightMin'] > \
			config['lorryMaxLoad']:
			# this is a case when the max bags in the truck have greater weight than
			# the truck can handle
			self.validate_warnings.append(Simulation.BIN_WEIGHT_LORRY_WARNING)

		if config['warmUpTime'] >= config['stopTime']:
			self.validate_warnings.append(Simulation.STATISTICS_WARNING)
		
		# are indices should not have duplicates
		area_indices = []

		for area_config in config['areas']:
			if area_config['areaIdx'] in area_indices:
				self.validate_errors.append(Simulation.DUPLICATE_AREA_INDEX.format(area_config['areaIdx']))
				return False

			if area_config['areaIdx'] >= config['noAreas']:
				self.validate_errors.append(Simulation.INVALID_AREA_INDEX.format(area_config['areaIdx']))
				return False

			area_indices.append(area_config['areaIdx'])

			if area_config['serviceFreq'] > config['disposalDistrRate']:
				# This means we dispose of bags more frequently than we service them
				self.validate_warnings.append(Simulation.DISPOSAL_FREQUENCY_WARNING.format(
					area_config['areaIdx']
				))

			if area_config['thresholdVal'] > 1:
				self.validate_errors.append(Simulation.BAD_THRESHOLD_VAL.format(area_config['areaIdx']))
				return False
				
		if len(area_indices) < config['noAreas']:
			self.validate_errors.append(Simulation.MISSING_AREAS)
			return False

		return True

	def _init_initial_events(self):
		"""
			This initializes bin disposal events, which will start
			the entire simulation run. Neat :)
		"""

		for area in self.areas:
			area.init()

	def reset(self, config):
		for i in xrange(0, self.config['noAreas']):
			# instantiate all areas with their respective configurations
			area_config = deepcopy(config)

			# copy area-specific properties to its config
			for key, val in area_config['areas'][i].items():
				if key not in area_config:
					area_config[key] = val

			# remove the overall configuration
			del area_config['areas']
			self.areas[i].reset(area_config)


	def run(self):
		if self.simulation_aborted:
			return
		
		# finally, start the simulation
		self._init_initial_events()
