class InputParser:
	"""Parses an input file and returns a configuration object."""

	UNRECOGNIZED_PARAMETER_WARNING = "Parse Warning({0}): parameter {1} is not recognized."
	MALFORMED_PARAMETER_ERROR = "Parse Error({0}): parameter {1} is malformed."
	CONVERSION_ERROR = "Parse Error({0}): Wrong type given for value(s) of {1}."
	ROADS_LAYOUT_ERROR = "Parse Error({0}): The roads layout for area {1} is malformed."
	ROADS_LAYOUT_EXPECTED = "Parse Error({0}): Expected 'roadsLayout' after are definition."
	ROADS_LAYOUT_UNEXPECTED = "Parse Error({0}): Expected 'areaIdx' before 'roadsLayout'."
	BAD_PARAMETER_VALUE = "Parse Error({0}): Bad value for parameter {1}."

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

		self.config = {
			areas: []
		}
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

		# if any are False, add a conversion Error
		if (any[val == False for val in param_values])
			self.parseErrors.append(
				CONVERSION_ERROR.format(lineNo, params[0])
			)
			return False

		config.ares.append(dict(zip(param_names, param_values)))

		return True
		
	def _parse_roads_layout(self, lineNo, lines, areaConfig):
		adj_list = [[]] * areaConfig.noBins

		for (current_bin, l) in enumerate(lines):
			l = [_cast_value('int', l) for l in lines]

			# check for adjacency length
			if len(l) != areaConfig.noBins:
				self.parseErrors.append(
					ROADS_LAYOUT_ERROR.format(lineNo + current_bin, areaConfig.areaIdx)
				)
				return False

			# check for invalid values
			if any[val == False or val < -1 for val in l]:
				self.parseErrors.append(
					CONVERSION_ERROR.format(lineNo + current_bin, 'roadsLayout')
				)
				return False

			for (idx, path_length) in enumerate(l):
				# check that the distance from bin idx to itself is 0
				if idx == current_bin and path_length != 0:
					self.parseErrors.append(
						CONVERSION_ERROR.format(lineNo + current_bin, 'roadsLayout')
					)
					return False

				if path_length != -1:
					adj_list[current_bin].append({
						'bin_index': idx,
						'path_length': path_length
					})

		areaConfig.roadsLayout = adj_list
		return True

	# TODO: function larger than one screen, refactor
	def parse(self):
		# open the file in read only mode
		with open(self.file_name) as f:
			lines = f.readlines()

		skipUntil = -1

		for idx, line in enumerate(lines):
			if skipUntil != -1 and idx < skipUntil:
				continue
			
			# split by space. The default method
			#	will remove any extra whitespaces
			params = line_clean.split(None)
			
			# comments, this deals with both
			# `#comment`
			# `# comment`
			if params[0][0] == '#':
				continue

			param_name = params[0]
			# non-existing parameters are ignored with a warning
			if param_name not in InpuParser._parameters_map:
				self.parseWarnings.append(NON_EXISTING_PARAMETER_WARNING.format(idx, param_name))

			# this cannot happen, we need an area_idx before the roadsLayout
			if param_name == 'roadsLayout':
				self.parseErrors.append(ROADS_LAYOUT_UNEXPECTED.format(idx))
				return False

			# areaIdx and roadsLayout are special cases
			if param_name == 'areaIdx':
				status = self._parse_area_idx(idx, params, self.config)
				if not status:
					return False

				# then expect the next noBins to be a roadsLayout
				if idx + 2 >= len(lines) or lines[idx + 1] != 'roadsLayout':
					self.parseErrors(ROADS_LAYOUT_EXPECTED.format(idx + 1))
					return False

				# get the last area
				lastArea = config.areas[-1]
				# we expect a noBins x noBins array
				if lastArea.noBins + idx + 2 >= len(lines):
					self.parseErrors(ROADS_LAYOUT_ERROR.format(idx + 2, lastArea.aredIdx))
					return False
				
				# skip these here
				# TODO: this seems a little ugly, refactor
				skipUntil = idx + 2 + lastArea.noBins

				# parse the layout
				status = self._parse_roads_layout(lineNo, lines[idx + 2, idx + 2 + lastArea.noBins], lastArea)
				if not status:
					return False

				continue
			
			# handle all 'simple' parameters
			if len(params) > 2:
				self.parseErrors.append(MALFORMED_PARAMETER_ERROR.format(idx, param_name))
				return False

			param_value = InputParser._cast_value(InputParse._parameters_map[param_name], params[1])
			if param_value == False:
				self.parseErrors.append(BAD_PARAMETER_VALUE.format(idx, param_name))
				return False

			# add the parameter value
			self.config[param_name] = param_value
			
		return True