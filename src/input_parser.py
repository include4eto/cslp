class InputParser:
	"""Parses an input file and returns a configuration object."""

	UNRECOGNIZED_PARAMETER_WARNING = "Parse Warning({0}): parameter {1} is not recognized."
	MALFORMED_PARAMETER_ERROR = "Parse Error({0}): parameter {1} is malformed."
	CONVERSION_ERROR = "Parse Error({0}): Wrong type given for value(s) of {1}."

	# Map from name to type, so we know how to parse.
	# 	<name>: <expected_type>
	# NOTE: We don't distinguish between integer types,
	#	uint8 or uint16
	_parameters_map = {
		'lorryVolume': 'int',
		'lorryMaxLoad': 'int',
		'binServiceTime': 'float',
		'binVolume': 'float',
		'disposalDistrRate': 'float',
		'disposalDistrShape': 'int',
		'bagVolume': 'float',
		'bagWeightMin': 'float',
		'bagWeightMax': 'float',
		'noAreas': 'int',
		'areaIdx': {
			'areaIdx': 'int',
			'serviceFreq': 'float',
			'thresholdVal': 'float',
			'noBins': 'int'
		},
		'roadsLayout': 'roads_layout',
		'stopTime': 'float',
		'warmUpTime': 'float'
	}

	def __init__(self, file_name):
		self.file_name = file_name

		self.config = {}
		"""The parsed configuration object"""

		self.parseErrors = []
		"""The parse errors"""

		self.parseWarnings = []
		"""The parse warnings"""

	@classmethod
	def _cast_value(type, value):
		try:
			# NOTE to self: there might be a better way to do this
			if type == 'int':
				return int(value)
			if type == 'float':
				return float(value)
		except ValueError:
			return False
		

	# TODO: maybe remove lineNo, it might not be a good idea
	#	for it to be passed as an argument
	def _parse_area_idx(self, lineNo, params, config):
		"""Parses the area_idx parameter"""

		# parameters should be a list of tuples, as such
		#	the length should be divisible by 2
		if length(params) % 2 != 0:
			self.parseWarnings.append(
				MALFORMED_PARAMETER_ERROR.format(lineNo, params[0])
			)
			return False

		_config = InputParser._parameters_map['areaIdx']
		# every even element is a key (parameter name)
		param_names = params[0::2]
		# every odd element should be a value
		param_values = [InputParser._cast_value(x) for x in params[1::2]]

		# if any are False, display a conversion Error
		if (any[val == False for val in param_values])
			self.parseWarnings.append(
				CONVERSION_ERROR.format(lineNo, params[0])
			)
			return False

		config.area_idx = dict(zip(param_names, param_values))

		return True

	@classmethod
	def _parse_roads_layout(layout):
		"""Parses the roads layout. Returns a layout dictionary."""
		pass

	

	def parse(self):
		# open the file in read only mode
		with open(self.file_name) as f:
			lines = f.readlines()

		for idx, line in enumerate(lines):
			# split by space. The default method
			#	will remove any extra whitespaces
			attrs = line_clean.split(None)
			
			# comments, this deals with both
			# `#comment`
			# `# comment`
			if attrs[0][0] == '#':
				continue

			attr_name = attrs[0]
			# non-existing parameters are ignored with a warning
			if attr_name not in InpuParser._parameters_map:
				self.parseWarnings.append(NON_EXISTING_PARAMETER_WARNING.format(idx, attr_name))

			# areaIdx and roadsLayout are special cases
			if attr_name == 'areaIdx':
				status = InputParser._parse_area_idx(idx, attrs, self.config)
				if not status:
					return False

				continue
			
			# 
			
