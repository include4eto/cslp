import unittest
import sys
from cslp.statistics.statistics_aggregator import StatisticsAggregator
from cslp.simulation.event_dispatcher import Event, EventDispatcher
from StringIO import StringIO

class StatisticsAggregatorTest(unittest.TestCase):
	"""Tests the aggregated statistics class"""

	config = {
		'noAreas': 2,
		'warmUpTime': 0.00001,
		'areas': [
			{
				'noBins': 3
			},
			{
				'noBins': 2
			}
		]
	}

	def test_trip_duration(self):
		dispatcher = EventDispatcher(100, 2)
		statistics_aggregator = StatisticsAggregator(StatisticsAggregatorTest.config, dispatcher)

		dispatcher.events = [
			# disposal at 1, no overflows
			Event(time = 1, area_index = 0, type = 'service_time'),
			
			# lower the total service time
			Event(time = 1, area_index = 1, type = 'service_time'),

			Event(time = 1, area_index = 0, type = 'bins_overflowed_at_service_time', data = { 'no_bins': 1 }),
			Event(time = 1, area_index = 0, type = 'lorry_departure', data = { 'lorry_idx': 0, 'location': 0 }),
			
			# arrival at bin 1
			Event(time = 2, area_index = 0, type = 'lorry_arrival', data = { 'lorry_idx': 0, 'location': 1 }),
			
			# empty the bin after 1 second
			Event(time = 3, area_index = 0, type = 'lorry_load_changed', data = {
				'lorry_id': 0,
				'bin_idx': 0,
				'lorry_volume': 5,
				'lorry_weight': 6
			}),

			# depart from the bin
			Event(time = 3, area_index = 0, type = 'lorry_departure', data = { 'lorry_idx': 0, 'location': 1 }),

			# arrive at 0
			Event(time = 4, area_index = 0, type = 'lorry_arrival', data = { 'lorry_idx': 0, 'location': 0 }),
			Event(time = 4, area_index = 0, type = 'lorry_load_changed', data = {
				'lorry_id': 0,
				'bin_idx': 0,
				'lorry_volume': 5,
				'lorry_weight': 6
			}),
		]

		for i in xrange(9):
			time = dispatcher.next_event()

		sys_stdout = sys.stdout

		captured_out = StringIO()
		sys.stdout = captured_out
		statistics_aggregator.print_output()
		
		self.assertEqual(captured_out.getvalue(),
			"---\n" +
			"area 0: average trip duration 00:03\n" +
			"area 1: average trip duration 00:00\n" +
			# we have 2 areas, total average 1.5
			"overall average trip duration 00:03\n" +

			"area 0: average no. trips 1.000\n" +
			"area 1: average no. trips 0.000\n" +
			"overall average no. trips 0.500\n" +
			
			"area 0: trip efficiency 2.000\n" +
			"area 1: trip efficiency 0.000\n" +
			"overall trip efficiency 2.000\n" +
			
			"area 0: average volume collected 5.000\n" +
			"area 1: average volume collected 0.000\n" +
			"overall average volume collected 5.000\n" +
			
			"area 0: percentage of bins overflowed 33\n" +
			"area 1: percentage of bins overflowed 0\n" +
			"overall percentage of bins overflowed 16\n" +
			
			"---\n"
		)
		sys.stdout = sys_stdout
	# def test_
