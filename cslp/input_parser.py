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
	DUPLICATE_PARAMETER_ERROR = "Parse Error({0}): Duplicate parameter {1}"
	DUPLICATE_EXPERIMENT_ERROR = "Parse Error({0}): Duplicate experiment found: {1}"
	NON_EXPERIMENT_PARAMETER = "Parse Warning({0}): Parameter {1} can only be used in this context as an experiment. Experiment keyword missing."

	EXPERIMENT_KEYWORD = "experiment"

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
		'warmUpTime': 'float',

		'serviceFreq': 'float',
		'thresholdVal': 'float'
	}

	# parameters excluded from the required check
	_non_required_params = {
		'serviceFreq': 'float',
		'thresholdVal': 'float',
		'roadsLayout': 'roads_layout',
		'areaIdx': 'area_idx'
	}

	_extra_experiment_params = {
		'serviceFreq': 'float',
		'thresholdVal': 'float',
	}

	def __init__(self, file_name, treat_warnings_as_errors = True):
		self.file_name = file_name

		self.config = {
			'areas': [],
			'noAreas': False,
			'experiments': {}
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
		adj_list = []

		for (current_bin, line) in enumerate(lines):
			line = line.split()
			paths = [InputParser._cast_value('int', x) for x in line]
		
			# check for adjacency length
			if len(paths) != areaConfig['noBins'] + 1:
				self.parse_errors.append(InputParser.ROADS_LAYOUT_ERROR.format(lineNo + current_bin, areaConfig['areaIdx']))
				return False

			# check for invalid values
			if any([path is False or path < -1 for path in paths]):
				self.parse_errors.append(InputParser.CONVERSION_ERROR.format(lineNo + current_bin, 'roadsLayout'))
				return False

			adj_list_bin = []
			for (idx, path_length) in enumerate(paths):
				# check that the distance from bin idx to itself is 0
				if idx == current_bin and path_length != 0:
					self.parse_errors.append(InputParser.CONVERSION_ERROR.format(lineNo + current_bin, 'roadsLayout'))
					return False

				if path_length != -1:
					adj_list_bin.append({
						'index': idx,
						'path_length': path_length
					})

			adj_list.append(adj_list_bin)
		areaConfig['roadsLayout'] = adj_list
		return True

	def _check_missing_parameters(self):
		# check we have all keys
		for (key, type) in InputParser._parameters_map.items():
			if key in InputParser._non_required_params:
				continue

			if key not in self.config and key not in self.config['experiments']:
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

	def _parse_experiment(self, idx, param_name, params):
		type = InputParser._parameters_map[param_name]
		# cast all the values for the experiment
		values = [InputParser._cast_value(type, x) for x in params]
		
		# check for invalid values
		if any([v is False for v in values]):
			self.parse_errors.append(InputParser.CONVERSION_ERROR.format(idx, param_name))
			return False
		
		# the parameter can be duplicated both in the general
		#	and experimentation config
		if (param_name in self.config['experiments']) or \
			(param_name in self.config and self.config[param_name] != False):
			self.parse_errors.append(InputParser.DUPLICATE_EXPERIMENT_ERROR.format(idx, param_name))
			return False

		self.config['experiments'][param_name] = values

		return True

	def _parse_param(self, idx, line):
		param_name = line[0]
		if line[1] == InputParser.EXPERIMENT_KEYWORD:
			return self._parse_experiment(idx, param_name, line[2::])

		if param_name in InputParser._extra_experiment_params:
			self.parse_warnings.append(InputParser.NON_EXPERIMENT_PARAMETER.format(idx, param_name))
			if self.treat_warnings_as_errors:
				return False

		# handle all 'simple' parameters
		if len(line) > 2:
			self.parse_errors.append(InputParser.MALFORMED_PARAMETER_ERROR.format(idx, param_name))
			return False

		param_value = InputParser._cast_value(InputParser._parameters_map[param_name], line[1])
		if param_value is False:
			self.parse_errors.append(InputParser.BAD_PARAMETER_VALUE.format(idx, param_name))
			return False

		# add the parameter value
		if (param_name in self.config and self.config[param_name] != False) or \
			(param_name in self.config['experiments']):
			self.parse_errors.append(InputParser.DUPLICATE_PARAMETER_ERROR.format(idx, param_name))
			return False
		self.config[param_name] = param_value

		return True

	def _parse_area_definition(self, idx, area_idx, lines):
		# to keep track where we are in the file
		line_count = len(lines)

		if self.config['noAreas'] == False:
			self.parse_errors.append(InputParser.MISSING_PARAM_ERROR.format('noAreas'))
			return (False, lines, 0)

		# check to see if more areas than defined
		if len(self.config['areas']) == self.config['noAreas']:
			self.parse_errors.append(InputParser.MORE_AREAS_SPECIFIED.format(idx, self.config['noAreas']))
			return (False, lines, 0)

		status = self._parse_area_idx(idx, area_idx)
		if not status:
			return (False, lines, 0)

		# get the last area
		lastArea = self.config['areas'][-1]

		# pop the 'roadsLayout' term
		rl = lines.pop(0)
		# +1 for the depot
		rl_shape = lastArea['noBins'] + 1

		# then expect the next noBins + 1 lines (for the depot) to be a roadsLayout
		if rl_shape > len(lines) or rl != 'roadsLayout':
			self.parse_errors.append(InputParser.ROADS_LAYOUT_EXPECTED.format(idx + 1))
			return (False, lines, 0)

		# parse the layout
		status = self._parse_roads_layout(idx, lines[0:rl_shape], lastArea)
		if not status:
			return (False, lines, 0)

		lines = lines[rl_shape:]
		return (True, lines, line_count - len(lines))
	
	@staticmethod
	def _sanitize(line):
		# strip multiple whitespaces/tabs/newline
		line_clean = re.sub(r'\n', '', line)
		line_clean = re.sub(r'\s+', ' ', line_clean)
		return line_clean


	# TODO: function larger than one screen, refactor
	def parse(self):
		# open the file in read only mode
		try:
			with open(self.file_name) as f:
				lines = f.readlines()
		except FileNotFoundError:
			self.parse_errors.append(InputParser.FILE_NOT_FOUND.format(self.file_name))
			return False
		
		# comments, this deals with both
		# `#comment`
		# `# comment`
		lines = [InputParser._sanitize(line) for line in lines if (line[0] != '#' and len(line) > 1)]

		idx = 0
		while len(lines) > 0:
			line = lines.pop(0)
			idx += 1
			
			# split by space. The default method
			#	will remove any extra whitespaces
			params = line.split(None)
			if len(params) == 0:
				continue

			param_name = params[0]
			# non-existing parameters are ignored with a warning
			if param_name not in InputParser._parameters_map:
				self.parse_warnings.append(InputParser.UNRECOGNIZED_PARAMETER_WARNING.format(idx, param_name))
				if self.treat_warnings_as_errors:
					return False	
				else:
					continue

			# this cannot happen, we need an area_idx before the roadsLayout
			if param_name == 'roadsLayout':
				self.parse_errors.append(InputParser.ROADS_LAYOUT_UNEXPECTED.format(idx))
				return False

			# areaIdx and roadsLayout are special cases
			if param_name == 'areaIdx':
				status, lines, l = self._parse_area_definition(idx, params, lines)

				# do this so we can keep track where we are in the file (to report errors)
				idx += l
				if status == False:
					return False
				
				continue
				
			if self.config['noAreas'] != False and len(self.config['areas']) != self.config['noAreas']:
				self.parse_errors.append(InputParser.AREAS_DEFINITION_INCOMPLETE.format(idx, param_name))
				return False
			
			res = self._parse_param(idx, params)
			if not res:
				return False
			
		return self._check_missing_parameters()