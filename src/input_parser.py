class InputParser:
	"""Parses an input file and returns a configuration object."""

	NON_EXISTING_ATTRIBUTE_WARNING = "Parse Warning({0}): attribute {1} is not recognized."

	# Map from name to type, so we know how to parse.
	# 	<name>: <expected_type>
	# NOTE: We don't distinguish between integer types,
	#	uint8 or uint16
	attribute_map = {
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

	def _roads_layout(self, layout):
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
			# non-existing attributes are ignored with a warning
			if attr_name not in attribute_map:
				print(NON_EXISTING_ATTRIBUTE_WARNING.format(idx, attr_name))
			
			
