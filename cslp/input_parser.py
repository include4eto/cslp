import re

class InputParser:
	"""
		Parses an input file and returns a configuration object.
		Note the parser does not check constraints on values except for types.
		This would raise a Configuration Error, rather than a parse error and that
			is with the application itself, *not* the parser.
	"""

	UNRECOGNIZED_PARAMETER_WARNING = "Parse Warning({0}): parameter {1} is not recognized."
	MALFORMED_PARAMETER_ERROR = "Parse Error({0}): parameter {1} is malformed."
	CONVERSION_ERROR = "Parse Error({0}): Wrong type given for value(s) of {1}."
	ROADS_LAYOUT_ERROR = "Parse Error({0}): The roads layout for area {1} is malformed."
	ROADS_LAYOUT_EXPECTED = "Parse Error({0}): Expected 'roadsLayout' after area definition."
	ROADS_LAYOUT_UNEXPECTED = "Parse Error({0}): Expected 'areaIdx' before 'roadsLayout'."
	BAD_PARAMETER_VALUE = "Parse Error({0}): Bad value for parameter {1}."
	MORE_AREAS_SPECIFIED = "Parse Error({0}): Too many areas. Max is {1}."
	LESS_AREAS_SPECIFIED = "Parse Warning: Not enough areas. noAreas is {0}."
	AREAS_DEFINITION_INCOMPLETE = "Parse Error({0}): Expected area definition, got ({1})."
	MISSING_PARAM_ERROR = "Parse Error: Missing parameter {0}."
	FILE_NOT_FOUND = "Parse Error: No such file: {0}."

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

	def __init__(self, file_name, treat_warnings_as_errors = True):
		self.file_name = file_name

		self.config = {
			'areas': [],
			'noAreas': False
		}
		"""The parsed configuration object"""

		self.parse_errors = []
		"""The parse errors"""

		self.parse_warnings = []
		"""The parse warnings"""

		self.treat_warnings_as_errors = treat_warnings_as_errors

	@staticmethod
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
	def _parse_area_idx(self, lineNo, params):
		"""Parses the area_idx parameter"""

		# parameters should be a list of tuples, as such
		#	the length should be divisible by 2
		if len(params) % 2 != 0:
			self.parse_warnings.append(
				InputParser.MALFORMED_PARAMETER_ERROR.format(lineNo, params[0])
			)

			if self.treat_warnings_as_errors:
				return False

		_config = InputParser._parameters_map['areaIdx']
		# every even element is a key (parameter name)
		param_names = params[0::2]
		# every odd element should be a value
		param_values = params[1::2]
		params = zip(param_names, param_values)

		try:
			params = [(p[0], InputParser._cast_value(_config[p[0]], p[1])) for p in params]
		except KeyError:
			# this means that the value doesn't exist in the configuration object
			self.parse_errors.append(
				InputParser.MALFORMED_PARAMETER_ERROR.format(lineNo, 'areaIdx')
			)
			return False

		# if any are False, add a conversion Error
		if any([p[1] is False for p in params]):
			self.parse_errors.append(
				InputParser.CONVERSION_ERROR.format(lineNo, 'areaIdx')
			)
			return False

		self.config['areas'].append(dict(params))

		return True
		
	def _parse_roads_layout(self, lineNo, lines, areaConfig):
		adj_list = [[]] * areaConfig['noBins']

		for (current_bin, line) in enumerate(lines):
			line = line.split()
			paths = [InputParser._cast_value('int', x) for x in line]
		
			# check for adjacency length
			if len(paths) != areaConfig['noBins'] + 1:
				self.parse_errors.append(
					InputParser.ROADS_LAYOUT_ERROR.format(lineNo + current_bin, areaConfig['areaIdx'])
				)
				return False

			# check for invalid values
			if any([path is False or path < -1 for path in paths]):
				self.parse_errors.append(
					InputParser.CONVERSION_ERROR.format(lineNo + current_bin, 'roadsLayout')
				)
				return False

			for (idx, path_length) in enumerate(paths):
				# check that the distance from bin idx to itself is 0
				if idx == current_bin and path_length != 0:
					self.parse_errors.append(
						InputParser.CONVERSION_ERROR.format(lineNo + current_bin, 'roadsLayout')
					)
					return False

				if path_length != -1:
					adj_list[current_bin].append({
						'bin_index': idx,
						'path_length': path_length
					})

		areaConfig['roadsLayout'] = adj_list
		return True

	def _check_missing_parameters(self):
		# check we have all keys
		for (key, type) in InputParser._parameters_map.items():
			if key == 'areaIdx' or key == 'roadsLayout':
				continue

			if key not in self.config:
				self.parse_errors.append(
					InputParser.MISSING_PARAM_ERROR.format(key)
				)
				return False

		# check we have enough areas
		if len(self.config['areas']) < self.config['noAreas']:
			err_msg = InputParser.LESS_AREAS_SPECIFIED.format(self.config['noAreas'])

			# if we have some areas, then we can continue and it's only a warning
			if len(self.config['areas']) == 0:
				self.parse_errors.append(err_msg)
				return False
			else:
				self.parse_warnings.append(err_msg)
				if self.treat_warnings_as_errors:
					return False

			return False

		return True

	# TODO: function larger than one screen, refactor
	def parse(self):
		# open the file in read only mode
		try:
			with open(self.file_name) as f:
				lines = f.readlines()
		except FileNotFoundError:
			self.parse_errors.append(
				InputParser.FILE_NOT_FOUND.format(self.file_name)
			)
			return False

		skipUntil = -1
		# comments, this deals with both
		# `#comment`
		# `# comment`
		lines = [line for line in lines if line[0] != '#']

		for idx, line in enumerate(lines):
			if skipUntil != -1 and idx < skipUntil:
				continue

			# strip multiple whitespaces/tabs/newline
			line_clean = re.sub(r'\n', '', line)
			line_clean = re.sub(r'\s+', ' ', line_clean)
			
			# split by space. The default method
			#	will remove any extra whitespaces
			params = line_clean.split(None)
			if len(params) == 0:
				continue

			param_name = params[0]
			# non-existing parameters are ignored with a warning
			if param_name not in InputParser._parameters_map:
				self.parse_warnings.append(
					InputParser.UNRECOGNIZED_PARAMETER_WARNING.format(idx, param_name)
				)
				continue

			# this cannot happen, we need an area_idx before the roadsLayout
			if param_name == 'roadsLayout':
				self.parse_errors.append(InputParser.ROADS_LAYOUT_UNEXPECTED.format(idx))
				return False

			# areaIdx and roadsLayout are special cases
			if param_name == 'areaIdx':
				# check to see if more areas than defined
				if len(self.config['areas']) == self.config['noAreas']:
					self.parse_errors.append(
						InputParser.MORE_AREAS_SPECIFIED.format(idx, self.config['noAreas'])
					)

				status = self._parse_area_idx(idx, params)
				if not status:
					return False

				# then expect the next noBins to be a roadsLayout
				if idx + 2 >= len(lines) or lines[idx + 1] != 'roadsLayout\n':
					self.parse_errors.append(InputParser.ROADS_LAYOUT_EXPECTED.format(idx + 1))
					return False

				# get the last area
				lastArea = self.config['areas'][-1]
				# we expect a noBins x noBins array
				if lastArea['noBins'] + idx + 2 >= len(lines):
					self.parse_errors.append(InputParser.ROADS_LAYOUT_ERROR.format(idx + 2, lastArea['areaIdx']))
					return False
				
				# skip these here
				# TODO: this seems a little ugly, refactor
				skipUntil = idx + 2 + lastArea['noBins'] + 1

				# parse the layout
				status = self._parse_roads_layout(idx, lines[idx + 2 : idx + 2 + lastArea['noBins']], lastArea)
				if not status:
					return False

				continue
			
			# handle all 'simple' parameters
			if len(params) > 2:
				self.parse_errors.append(InputParser.MALFORMED_PARAMETER_ERROR.format(idx, param_name))
				return False
				
			if self.config['noAreas'] != False and len(self.config['areas']) != self.config['noAreas']:
				self.parse_errors.append(
					InputParser.AREAS_DEFINITION_INCOMPLETE.format(idx, param_name)
				)


			param_value = InputParser._cast_value(InputParser._parameters_map[param_name], params[1])
			if param_value is False:
				self.parse_errors.append(InputParser.BAD_PARAMETER_VALUE.format(idx, param_name))
				return False

			# add the parameter value
			self.config[param_name] = param_value
			
		return self._check_missing_parameters()