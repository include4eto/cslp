#!/usr/bin/env python2.7
import unittest
import pprint
from cslp.input_parser import InputParser 

class InputParserTest(unittest.TestCase):
	"""Test the input parser with specific files and an expected config"""

	pp = pprint.PrettyPrinter(indent = 2)

	def test_valid_input(self):
		# checks that a valid simple input is parsed
		parser = InputParser('test/inputs/parser_tests/basic_input.txt')
		result = parser.parse()
		# this is the expected configuration of the input
		expected_config = {
			'experiments': {},
			'lorryVolume': 20,
			'lorryMaxLoad': 7000,
			'binServiceTime': 130,
			'binVolume': 2,
			'disposalDistrRate': 2.0,
			'disposalDistrShape': 2,
			'bagVolume': 0.05,
			'bagWeightMin': 2,
			'bagWeightMax': 8,
			'stopTime': 36.0,
			'warmUpTime': 12.0,
			'noAreas': 1,
			'areas': [
				{
					'noBins': 5,
					'serviceFreq': 0.0625,
					'thresholdVal': 0.75,
					'areaIdx': 0,
					'roadsLayout': [
						[
							{ 'index': 0, 'path_length': 0 },
						 	{ 'index': 1, 'path_length': 3 },
						 	{ 'index': 5, 'path_length': 4 }
						],
						[
							{ 'index': 0, 'path_length': 3 },
							{ 'index': 1, 'path_length': 0 },
							{ 'index': 2, 'path_length': 5 }
						],
						[
							{ 'index': 2, 'path_length': 0 },
							{ 'index': 3, 'path_length': 2 },	
						],
						[
							{ 'index': 3, 'path_length': 0 },
							{ 'index': 4, 'path_length': 2 },
							{ 'index': 5, 'path_length': 2 },	
						],
						[
							{ 'index': 1, 'path_length': 1 },
							{ 'index': 4, 'path_length': 0 }
						],
						[
							{ 'index': 0, 'path_length': 4 },
							{ 'index': 3, 'path_length': 2 },
							{ 'index': 4, 'path_length': 4 },
							{ 'index': 5, 'path_length': 0 },
						]
					]
				}
			]
		}

		self.assertEqual(expected_config, parser.config)
		self.assertTrue(result)
	
	def test_invalid_input(self):
		# check against an invalid simple input
		parser = InputParser('test/inputs/parser_tests/invalid.in.txt')
		result = parser.parse()

		self.assertFalse(result)

	def test_grid_input(self):
		# a grid input with big areas, still valid
		parser = InputParser('test/inputs/parser_tests/grids.dat.txt')
		result = parser.parse()

		self.assertTrue(result)

	def test_valid_many(self):
		# a test input with many valid areas
		parser = InputParser('test/inputs/parser_tests/valid_many_areas.txt')
		result = parser.parse()
		pprint.pprint(parser.parse_errors)

		self.assertTrue(result)

	def test_invalid_roads(self):
		# a test input with valid parameters, but invalid roads layout
		parser = InputParser('test/inputs/parser_tests/invalid_roads_layout.txt')
		result = parser.parse()

		self.assertFalse(result)

	def test_experimentation(self):
		# a valid experimentation input
		parser = InputParser('test/inputs/parser_tests/experiment_input.txt')
		result = parser.parse()
		
		self.assertTrue(result)

	def test_magnitude_violation(self):
		# tests a validly formatted input, but
		# 	with wrong ranges
		parser = InputParser('test/inputs/parser_tests/invalid_magnitude.txt')
		result = parser.parse()

		self.assertFalse(result)

	def test_extra_parameters(self):
		# test that extra paratemeters are not allowed

		parser = InputParser('test/inputs/parser_tests/extra_parameters.txt')
		result = parser.parse()

		self.assertFalse(result)
	
	def test_invalid_matrix(self):
		# test that all paths should be greater than 0 apart from the diagonal

		parser = InputParser('test/inputs/parser_tests/test_invalid_matrix.txt')
		result = parser.parse()

		self.assertFalse(result)
	
	
	def test_max_magnitude(self):
		# test that the maximum magnitudes are allowed
		parser = InputParser('test/inputs/parser_tests/max_magnitudes.txt')
		result = parser.parse()

		self.assertTrue(result)
	
	def test_whitespaces(self):
		# test that more than one whitespaces are stripped
		#	this includes tabs, but not new lines 
		parser = InputParser('test/inputs/parser_tests/whitespaces.txt')
		result = parser.parse()

		self.assertTrue(result)
	