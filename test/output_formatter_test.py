#!/usr/bin/env python2.7
import unittest
import pprint
from cslp.output_formatter import OutputFormatter 
from cslp.simulation.event_dispatcher import Event, EventDispatcher
from StringIO import StringIO
import sys

class OutputFormatterTest(unittest.TestCase):
	"""
		Tests the output formatter class.
	"""

	# dispatcher to be used throughout the suite
	dispatcher = EventDispatcher(100, 4)

	def test_time_formatting(self):
		"""
			Tests various time formats for correct conversion to DD:HH:MM:SS
		"""
		of = OutputFormatter(OutputFormatterTest.dispatcher)
		
		self.assertEquals(of._format_time(1432), '00:00:23:52')
		self.assertEquals(of._format_time(88888888), '1028:19:21:28')
		self.assertEquals(of._format_time(0), '00:00:00:00')
		self.assertEquals(of._format_time(60), '00:00:01:00')
		self.assertEquals(of._format_time(24 * 60 * 60), '01:00:00:00')
	
	
	def test_bin_output_events(self):
		"""
			Tests various output events for correct formatting.
		"""
		dispatcher = OutputFormatterTest.dispatcher
		of = OutputFormatter(OutputFormatterTest.dispatcher)

		dispatcher.events = [
			Event(time = 10, area_index = 0, type = 'bin_disposal', data = { 'bin_idx': 0, 'bag_vol': 5, 'bag_weight': 20}),
			Event(time = 15, area_index = 1, type = 'bin_load_changed', data = { 'bin_idx': 1, 'bin_volume': 2, 'bin_weight': 3}),
			Event(time = 20, area_index = 2, type = 'bin_occupancy_exceeded', data = { 'bin_idx': 0, 'occupancy': 1.2 }),
			Event(time = 25, area_index = 3, type = 'bin_overflow', data = { 'bin_idx': 0, 'occupancy': 0.7})
		]

		# capture stdout
		sys_stdout = sys.stdout
		captured_out = StringIO()
		sys.stdout = captured_out

		# progress time
		dispatcher.next_event()
		# restore stdout so assert errors work & assert
		sys.stdout = sys_stdout
		self.assertEqual(captured_out.getvalue(), '00:00:00:10 -> bag weighing 20.000 kg disposed of at bin 0.0\n')

		# repeat for all events
		captured_out = StringIO()
		sys.stdout = captured_out
		dispatcher.next_event()
		sys.stdout = sys_stdout
		self.assertEqual(captured_out.getvalue(), '00:00:00:15 -> load of bin 1.1 became 3.000 kg and contents volume 2.000 m^3\n')
		
		# repeat for all events
		captured_out = StringIO()
		sys.stdout = captured_out
		dispatcher.next_event()
		sys.stdout = sys_stdout
		self.assertEqual(captured_out.getvalue(), '00:00:00:20 -> occupancy threshold of bin 2.0 exceeded\n')
		
		# repeat for all events
		captured_out = StringIO()
		sys.stdout = captured_out
		dispatcher.next_event()
		sys.stdout = sys_stdout
		self.assertEqual(captured_out.getvalue(), '00:00:00:25 -> bin 3.0 overflowed\n')
		


