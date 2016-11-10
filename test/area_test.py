#!/usr/bin/env python2.7
import unittest
import pprint
from cslp.simulation.area import Area
from cslp.simulation.event_dispatcher import Event, EventDispatcher
from copy import deepcopy

class AreaTest(unittest.TestCase):
	"""
		Area class test. Creates a valid event dispatcher
		and tests to see the area pushes the correct events.
	"""

	# a valid test configuration file
	# NOTE: This is not a valid input parser configuration,
	#	but rather a valid *AREA* configuration. It contains
	# 	all needed parameters plus the params for that specific area.
	test_area_config = {
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
		'stopTime': 36.0 * 60 * 60,
		'warmUpTime': 12.0,
		'noAreas': 1,
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

	def test_observer_subscription(self):
		"""
			Test that the area attaches an observer.
		"""

		# dispatcher & test area
		dispatcher = EventDispatcher(AreaTest.test_area_config['stopTime'],
			AreaTest.test_area_config['noAreas'])
		area = Area(AreaTest.test_area_config, dispatcher)
		area.init_disposal_events()

		# check the area has attached an observer
		self.assertNotEqual(len(dispatcher.observers), 0)

	def test_initial_disposal_events(self):
		"""
			Test that the area creates disposal events.	
		"""

		# dispatcher & test area
		dispatcher = EventDispatcher(AreaTest.test_area_config['stopTime'],
			AreaTest.test_area_config['noAreas'])
		area = Area(AreaTest.test_area_config, dispatcher)
		area.init_disposal_events()

		for e in dispatcher.events:
			# they should all be bin disposals and the time & weight,
			#	greater than 0
			self.assertEqual(e.type, 'bin_disposal')
			self.assertGreater(e.data['bag_weight'], 0)
			self.assertGreater(e.time, 0)

	def test_disposal_regeneration(self):
		"""
			Test that new bin events are generated.
		"""

		# dispatcher & test area
		dispatcher = EventDispatcher(AreaTest.test_area_config['stopTime'],
			AreaTest.test_area_config['noAreas'])
		area = Area(AreaTest.test_area_config, dispatcher)
		area.init_disposal_events()

		# now execute an event
		event = dispatcher.events[0]

		dispatcher.next_event()
		disposed_location = event.data['bin_idx']
		# filter events by bin
		new_events = [e for e in dispatcher.events if
			e.data['bin_idx'] == disposed_location and e.type == 'bin_disposal']
		self.assertEqual(len(new_events), 1)

	def test_overflow(self):
		"""
			Test that bins overflow
		"""
		overflow_config = deepcopy(AreaTest.test_area_config)
		# make bin overflow on first bag disposed
		overflow_config['binVolume'] = 1
		overflow_config['bagVolume'] = 2

		# dispatcher & test area
		dispatcher = EventDispatcher(overflow_config['stopTime'],
			overflow_config['noAreas'])
		area = Area(overflow_config, dispatcher)
		area.init_disposal_events()

		# now execute an event
		event = dispatcher.events[0]

		dispatcher.next_event()
		disposed_location = event.data['bin_idx']
		# filter events by bin
		new_events = [e for e in dispatcher.events if
			e.data['bin_idx'] == disposed_location and e.type == 'bin_overflow']
		self.assertEqual(len(new_events), 1)

	def test_occupancy_exceeded(self):
		"""
			Test that bins emit occupancy exceeded events.
		"""
		overflow_config = deepcopy(AreaTest.test_area_config)
		# make bin overflow on first bag disposed
		overflow_config['binVolume'] = 1

		# This won't overflow
		overflow_config['bagVolume'] = 0.9

		# dispatcher & test area
		dispatcher = EventDispatcher(overflow_config['stopTime'],
			overflow_config['noAreas'])
		area = Area(overflow_config, dispatcher)
		area.init_disposal_events()

		# now execute an event
		event = dispatcher.events[0]

		dispatcher.next_event()
		disposed_location = event.data['bin_idx']
		# filter events by bin
		# we should NOT get any overflows
		new_events = [e for e in dispatcher.events if
			e.data['bin_idx'] == disposed_location and e.type == 'bin_overflow']
		self.assertEqual(len(new_events), 0)

		# but we should get occupancy exceeded events
		new_events = [e for e in dispatcher.events if
			e.data['bin_idx'] == disposed_location and e.type == 'bin_occupancy_exceeded']
		self.assertEqual(len(new_events), 1)
