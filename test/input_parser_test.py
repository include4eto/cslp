import unittest
import pprint
from cslp.input_parser import InputParser 

class InputParserTest(unittest.TestCase):
	"""Test the input parser with specific files and an expected config"""

	pp = pprint.PrettyPrinter(indent = 2)

	def test_valid_input(self):
		parser = InputParser('test/inputs/basic_input.txt')
		result = parser.parse()

		self.assertTrue(result)
	
	def test_invalid_input(self):
		parser = InputParser('test/inputs/invalid.in.txt')
		result = parser.parse()

		self.assertFalse(result)

	def test_grid_input(self):
		parser = InputParser('test/inputs/grids.dat.txt')
		result = parser.parse()

		self.assertTrue(result)

	def test_valid_many(self):
		parser = InputParser('test/inputs/valid_many_areas.txt')
		result = parser.parse()
		pprint.pprint(parser.parse_errors)

		self.assertTrue(result)

	def test_invalid_rads(self):
		parser = InputParser('test/inputs/invalid_roads_layout.txt')
		result = parser.parse()

		# print(parser.parse_errors, parser.parse_warnings)
		self.assertFalse(result)

	def test_experimentation(self):
		parser = InputParser('test/inputs/experiment_input.txt')
		result = parser.parse()
		
		self.assertTrue(result)

	# def test_valid_simple(self):
