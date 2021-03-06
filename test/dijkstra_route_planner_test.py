#!/usr/bin/env python2.7
from cslp.simulation.route_planning.dijkstra_route_planner import DijkstraRoutePlanner
import unittest
from pprint import pprint

class DijkstraRoutePlannerTest(unittest.TestCase):
	# TODO: document

	def test_basic(self):
		DijkstraRoutePlanner.ALGORITHM = DijkstraRoutePlanner.ALGORITHM_GREEDY
		# Graph:
		roadsLayout = [
			# depot
			[
				{ 'index': 1, 'path_length': 1 },
				{ 'index': 2, 'path_length': 5 },
			],
			# bin 1
			[
				{ 'index': 2, 'path_length': 2 },
			],
			# bin 2
			[
				{ 'index': 0, 'path_length': 2 },
				{ 'index': 1, 'path_length': 10 },
				{ 'index': 3, 'path_length': 1 },
			],
			# bin 3
			[
				{ 'index': 1, 'path_length': 2 },
			]
		]

		bins = [
			{
				'idx': 1,
				'current_volume': 10, 
				'current_weight': 10,
				'has_exceeded_occupancy': True,
				'has_overflowed': False
			},
			{
				'idx': 2,
				'current_volume': 20, 
				'current_weight': 10,
				'has_exceeded_occupancy': True,
				'has_overflowed': False
			},
			{
				'idx': 3,
				'current_volume': 5, 
				'current_weight': 3,
				'has_exceeded_occupancy': False,
				'has_overflowed': False
			},
		]

		planner = DijkstraRoutePlanner(roadsLayout, 4)
		route = planner.get_route(bins, flatten_route=False)

		expected_route = [
			{ 'target': 1, 'service': False },
			{ 'target': 2, 'service': True, 'distance': 3 },
			{ 'target': 3, 'service': False },
			{ 'target': 1, 'service': True, 'distance': 3 },
			{ 'target': 2, 'service': False },
			{ 'target': 0, 'service': False, 'distance': 4 }
		]

		self.assertEquals(route, expected_route)

		# now test with the flattened route
		route = planner.get_route(bins, flatten_route=True)
		expected_route = [
			{ 'target': 2, 'service': True, 'distance': 3 },
			{ 'target': 1, 'service': True, 'distance': 3 },
			{ 'target': 0, 'service': False, 'distance': 4 }
		]

		self.assertEquals(route, expected_route)

	def test_priority_planner(self):
		DijkstraRoutePlanner.ALGORITHM = DijkstraRoutePlanner.ALGORITHM_PRIORITY
		# Graph:
		roadsLayout = [
			# bin 0
			[
				{ 'index': 1, 'path_length': 1 },
				{ 'index': 2, 'path_length': 5 },
			],
			# bin 1
			[
				{ 'index': 2, 'path_length': 2 },
			],
			# bin 2
			[
				{ 'index': 0, 'path_length': 2 },
				{ 'index': 1, 'path_length': 10 },
				{ 'index': 3, 'path_length': 1 },
			],
			# bin 3
			[
				{ 'index': 1, 'path_length': 2 },
			]
		]

		bins = [
			{
				'idx': 1,
				'current_volume': 10, 
				'current_weight': 10,
				'has_exceeded_occupancy': True,
				'has_overflowed': False
			},
			{
				'idx': 2,
				'current_volume': 20, 
				'current_weight': 10,
				'has_exceeded_occupancy': True,
				'has_overflowed': False
			},
			{
				'idx': 3,
				'current_volume': 5, 
				'current_weight': 3,
				'has_exceeded_occupancy': False,
				'has_overflowed': False
			},
		]

		planner = DijkstraRoutePlanner(roadsLayout, 4)
		route = planner.get_route(bins, flatten_route=False)

		# the priority algorithm should choose the closest path first
		expected_route = [
			{ 'target': 1, 'service': True, 'distance': 1 },
			{ 'target': 2, 'service': True, 'distance': 2 },
			{ 'target': 0, 'service': False, 'distance': 2 },
		]

		self.assertEquals(route, expected_route)

		# now test with the flattened route
		route = planner.get_route(bins, flatten_route=True)
		expected_route = [
			{ 'target': 1, 'service': True, 'distance': 1 },
			{ 'target': 2, 'service': True, 'distance': 2 },
			{ 'target': 0, 'service': False, 'distance': 2 },
		]

		self.assertEquals(route, expected_route)
