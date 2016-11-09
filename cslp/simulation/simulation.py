from .area import Area
from copy import deepcopy

class Simulation:
	LORRY_CAPACITY_WARNING = "Validation Warning: Lorry capacity is too small. Lorry might not be able to fit in a full bin."
	LORRY_WEIGHT_ERROR = "Validation Error: Minimum bag weight is greater than lorry volume."
	BIN_WEIGHT_WARNING = "Validation Warning: Maximum bin weight might be larger than lorry maximum load."
	BIN_WEIGHT_LORRY_WARNING = "Validation Warning: Lorry might not be able to fill its maximum volume due to weight constraints"
	STATISTICS_WARNING = "Validation Warning: Warm up time is greater than stop time. No statistics will be reported."
	DISPOSAL_FREQUENCY_WARNING = "Validation Warning (Area {0}): Disposal rate is greater than service rate. This might be a mistake."
	BAG_WEIGHT_MIN_MAX_ERROR = "Validation Error: Mimimum bag weight is greater than maximum bag weight."

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

		# TODO: Add configuration error checking
		self.areas = []

		for i in xrange(0, self.config['noAreas']):
			# instantiate all areas with their respective configurations
			area_config = deepcopy(self.config)

			# copy area-specific properties to its config
			for key, val in area_config['areas'][i].items():
				area_config[key] = val

			# remove the overall configuration
			del area_config['areas']

			# select only the roads layout that the are needs
			self.areas.append(Area(area_config, event_dispatcher))

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
		
		if (config['lorryVolume'] / (2 * config['bagVolume'])) * config['bagWeightMin'] > \
			config['lorryMaxLoad']:
			# this is a case when the max bags in the truck have greater weight than
			# the truck can handle
			self.validate_warnings.append(Simulation.BIN_WEIGHT_LORRY_WARNING)

		if config['warmUpTime'] >= config['stopTime']:
			self.validate_warnings.append(Simulation.STATISTICS_WARNING)
		
		for area_config in config['areas']:
			if area_config['serviceFreq'] > config['disposalDistrRate']:
				# This means we dispose of bags more frequently than we service them
				self.validate_warnings.append(Simulation.DISPOSAL_FREQUENCY_WARNING.format(
					area_config['areaIdx']
				))
				
		return True

	def _init_initial_events(self):
		"""
			This initializes bin disposal events, which will start
			the entire simulation run. Neat :)
		"""

		for area in self.areas:
			area.init_disposal_events()

	
	def run(self):
		# finally, start the simulation
		self._init_initial_events()
