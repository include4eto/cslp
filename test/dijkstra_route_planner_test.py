#!/usr/bin/env python2.7
from cslp.simulation.route_planning.dijkstra_route_planner import DijkstraRoutePlanner
import unittest
from pprint import pprint

class DijkstraRoutePlannerTest(unittest.TestCase):
	# TODO: document

	def test_basic(self):
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
				'idx': 1,
				'current_volume': 5, 
				'current_weight': 3,
				'has_exceeded_occupancy': False,
				'has_overflowed': False
			},
		]

		planner = DijkstraRoutePlanner(roadsLayout, 4, 30, 0.75)
		route = planner.get_route(bins)

		pprint(route)

		expected_route = [
			{ 'target': 0, 'service': False },
			{ 'target': 1, 'service': False },
			{ 'target': 2, 'service': True },
			{ 'target': 3, 'service': False },
			{ 'target': 1, 'service': True },
			{ 'target': 2, 'service': False },
			{ 'target': 0, 'service': False }
		]

		self.assertEquals(route, expected_route)