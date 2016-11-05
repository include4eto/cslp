from .area import Area
from copy import deepcopy

class Simulation:
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

		# TODO: Add configuration error checking
		self.areas = []

		for i in range(0, self.config['noAreas']):
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
		pass


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
