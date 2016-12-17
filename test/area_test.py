#!/usr/bin/env python2.7
import unittest
import pprint
from cslp.simulation.area import Area
from cslp.simulation.event_dispatcher import Event, EventDispatcher
from copy import deepcopy
from cslp.simulation.route_planning.dijkstra_route_planner import DijkstraRoutePlanner

class DummyRoutePlanner:
	def __init__(self, area_map, total_nodes, lorry_capacity = None, threshold_val = None):
		pass
	def get_route(self, bins, flatten_route=False):
		return False
	def get_route_to_depot(self, source, include_source = False, flatten_route = False):
		return False

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
				{ 'index': 1, 'path_length': 3 },
				{ 'index': 5, 'path_length': 4 }
			],
			[
				{ 'index': 0, 'path_length': 3 },
				{ 'index': 2, 'path_length': 5 }
			],
			[
				{ 'index': 3, 'path_length': 2 },	
			],
			[
				{ 'index': 4, 'path_length': 2 },
				{ 'index': 5, 'path_length': 2 },	
			],
			[
				{ 'index': 1, 'path_length': 1 },
			],
			[
				{ 'index': 0, 'path_length': 4 },
				{ 'index': 3, 'path_length': 2 },
				{ 'index': 4, 'path_length': 4 },
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
		area = Area(AreaTest.test_area_config, dispatcher, DummyRoutePlanner)
		area.init()

		# check the area has attached an observer
		self.assertNotEqual(len(dispatcher.observers), 0)

	def test_initial_disposal_events(self):
		"""
			Test that the area creates disposal events.	
		"""

		# dispatcher & test area
		dispatcher = EventDispatcher(AreaTest.test_area_config['stopTime'],
			AreaTest.test_area_config['noAreas'])
		area = Area(AreaTest.test_area_config, dispatcher, DummyRoutePlanner)
		area.init()

		new_events = [e for e in dispatcher.events if e.type == 'bin_disposal']
		self.assertGreater(len(new_events), 0)

		for e in dispatcher.events:
			# they should all be bin disposals and the time & weight,
			#	greater than 0
			if e.type == 'bin_disposal':
				self.assertGreater(e.data['bag_weight'], 0)
				self.assertGreater(e.time, 0)

	def test_disposal_generation(self):
		"""
			Test that new bin events are generated.
		"""

		# dispatcher & test area
		dispatcher = EventDispatcher(AreaTest.test_area_config['stopTime'],
			AreaTest.test_area_config['noAreas'])
		area = Area(AreaTest.test_area_config, dispatcher, DummyRoutePlanner)
		area.init()

		# now execute an event
		event = dispatcher.events[0]

		dispatcher.next_event()
		disposed_location = event.data['bin_idx']
		# filter events by bin
		new_events = [e for e in dispatcher.events if
			e.type == 'bin_disposal' and e.data['bin_idx'] == disposed_location]
		
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
		area = Area(overflow_config, dispatcher, DummyRoutePlanner)
		area.init()

		# now execute an event
		event = dispatcher.events[0]

		dispatcher.next_event()
		disposed_location = event.data['bin_idx']
		# filter events by bin
		new_events = [e for e in dispatcher.events if
			e.type == 'bin_overflow' and e.data['bin_idx'] == disposed_location]
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
		area = Area(overflow_config, dispatcher, DummyRoutePlanner)
		area.init()

		# now execute an event
		event = dispatcher.events[0]

		dispatcher.next_event()
		disposed_location = event.data['bin_idx']
		# filter events by bin
		# we should NOT get any overflows
		new_events = [e for e in dispatcher.events if
			e.type == 'bin_overflow' and e.data['bin_idx'] == disposed_location]
		self.assertEqual(len(new_events), 0)

		# but we should get occupancy exceeded events
		new_events = [e for e in dispatcher.events if
			e.type == 'bin_occupancy_exceeded' and e.data['bin_idx'] == disposed_location]
		self.assertEqual(len(new_events), 1)

	def test_lorry_dispatch(self):
		config = {
			'lorryVolume': 2,
			'lorryMaxLoad': 7000,
			'binServiceTime': 130,
			'binVolume': 2,
			'disposalDistrRate': 2.0,
			'disposalDistrShape': 2,
			'bagVolume': 0.05,
			'bagWeightMin': 2,
			'bagWeightMax': 8,
			'stopTime': 360 * 60 * 60,
			'warmUpTime': 12.0,
			'noAreas': 1,
			'noBins': 5,
			'serviceFreq': 1,
			'thresholdVal': 0.75,
			'areaIdx': 0,
			'roadsLayout': [
				[
					{ 'index': 1, 'path_length': 2 },
					{ 'index': 2, 'path_length': 4 }
				],
				[
					{ 'index': 2, 'path_length': 1 },
				],
				[
					{ 'index': 0, 'path_length': 3 },
					{ 'index': 3, 'path_length': 2 },
				],
				[
					{ 'index': 2, 'path_length': 2 },
				]
			]
		}

		dispatcher = EventDispatcher(30000, 1)

		# the lorry will overflow trying to empty bin 3 that overflowed
		#	then it will need to go back to the depot
		area = Area(config, dispatcher, DijkstraRoutePlanner)

		dispatcher.events = [
			Event(time = 1, area_index = 0, type = 'service_time'),
		]

		# edit occupancies
		area.bins[2]['current_weight'] = 1
		area.bins[2]['current_volume'] = 3
		area.bins[2]['has_exceeded_occupancy'] = True
		
		# this will make the lorry overflow and need to go back
		#	to the depot
		area.bins[3]['current_weight'] = 5
		area.bins[3]['current_volume'] = 2
		area.bins[3]['has_exceeded_occupancy'] = True
		area.bins[3]['has_overflowed'] = True


		# service time event
		dispatcher.next_event()

		# lorry departure should be on top
		e = dispatcher.events[0]		
		self.assertEqual((e.time, e.type, e.data), (1, 'bins_overflowed_at_service_time', {
			'no_bins': 1
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (1, 'lorry_departure', {
			'location': 0,
			'lorry_idx': 0
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		# 3 min = 180sec here
		# first we arrive at bin 2, which we can empty
		self.assertEqual((e.time, e.type, e.data), (181, 'lorry_arrival', {
			'location': 2,
			'lorry_idx': 0
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (311, 'bin_emptied', {
			'location': 2,
			'lorry_idx': 0
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (311, 'bin_load_changed', {
			'bin_idx': 2,
			'bin_volume': 0,
			'bin_weight': 0,
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (311, 'lorry_load_changed', {
			'lorry_idx': 0,
			'lorry_volume': 1.5,
			'lorry_weight': 1,
		}))

		# then we arrive at bin 3, but cannot service it
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (311, 'lorry_departure', {
			'lorry_idx': 0,
			'location': 2
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (431, 'lorry_arrival', {
			'lorry_idx': 0,
			'location': 3
		}))

		# so we go back to 0
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (431, 'lorry_departure', {
			'lorry_idx': 0,
			'location': 3
		}))

		# and we arrive and reschedule
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (731, 'lorry_arrival', {
			'lorry_idx': 0,
			'location': 0
		}))

		# the trip is completed
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (731, 'trip_completed', {
			'lorry_idx': 0
		}))
		
		# the lorry is emptied after 5 * 130 = 650 seconds
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (1381, 'lorry_available', {
			'lorry_idx': 0
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (1381, 'lorry_load_changed', {
			'lorry_idx': 0,
			'lorry_volume': 0,
			'lorry_weight': 0
		}))

		# then we go straight to bin 3
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (1381, 'lorry_departure', {
			'lorry_idx': 0,
			'location': 0
		}))

		# this happens after 5 * 60 = 300 seconds
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (1681, 'lorry_arrival', {
			'lorry_idx': 0,
			'location': 3
		}))

		# then the bin is emptied, after 130 seconds
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (1811, 'bin_emptied', {
			'location': 3,
			'lorry_idx': 0
		}))

		# then the bin is emptied, after 130 seconds
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (1811, 'bin_load_changed', {
			'bin_idx': 3,
			'bin_volume': 0,
			'bin_weight': 0,
		}))

		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (1811, 'lorry_load_changed', {
			'lorry_idx': 0,
			# the volume is compressed
			'lorry_volume': 1,
			'lorry_weight': 5
		}))

		# then we go straight back to the depot
		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (1811, 'lorry_departure', {
			'lorry_idx': 0,
			'location': 3
		}))

		# after 300 seconds
		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (2111, 'lorry_arrival', {
			'lorry_idx': 0,
			'location': 0
		}))

		# the trip is completed
		dispatcher.next_event()
		e = dispatcher.events[0]
		self.assertEqual((e.time, e.type, e.data), (2111, 'trip_completed', {
			'lorry_idx': 0
		}))
		
		# and after 650 seconds, the lorry is available again
		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (2761, 'lorry_available', {
			'lorry_idx': 0
		}))

		# and its load changes to 0
		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (2761, 'lorry_load_changed', {
			'lorry_idx': 0,
			'lorry_volume': 0,
			'lorry_weight': 0
		}))

		# the next event should be the next service time, after one hour, at time 3601
		dispatcher.next_event()
		e = dispatcher.events[0]
		# service time is 130 seconds
		self.assertEqual((e.time, e.type, e.data), (3601, 'service_time', None))

