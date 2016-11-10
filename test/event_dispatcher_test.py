#!/usr/bin/env python2.7
import unittest
import pprint
from cslp.simulation.event_dispatcher import Event, EventDispatcher
from numpy.random import uniform 

class EventDispatcherTest(unittest.TestCase):
	"""Tests for the event dispatcher class."""

	def test_event_sorting(self):
		# dispatcher with one area
		dispatcher = EventDispatcher(1000, 1)

		# add some events
		iter, max = 10000, 999999
		for i in xrange(iter):
			time = int(uniform(0, max))
			dispatcher.add_event(Event(time))

		times = [x.time for x in dispatcher.events]
		# make sure events are sorted in time
		self.assertEqual(times, sorted(times))

	def test_basic_observer(self):
		observer = lambda x: self.assertEqual(x.type, 'test')

		# dispatcher with one area
		dispatcher = EventDispatcher(1000, 1)
		dispatcher.attach_observer(observer, 0)
		dispatcher.add_event(Event(time = 10, area_index = 0, type = 'test'))

		time = dispatcher.next_event()
		self.assertEqual(time, 10)

