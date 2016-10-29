from math import floor

class Event:
	"""Basic event"""

	def __init__(self, time, area_index = 0, type = 'none', data = None):
		# NOTE: time is *ALWAYS* in seconds. Since
		#	we use binary search here, this is fast. Swear on it!
		self.time = time
		self.area_index = area_index
		self.type = type
		self.data = data

class EventDispatcher:
	"""
		TODO
	"""

	def __init__(self, stop_time, no_areas):
		self.no_areas = no_areas
		self.observers = dict()
		self.stop_time = stop_time
		for i in range(0, self.no_areas):
			self.observers[i] = []

		# current time
		self.now = 0

		# Events are always sorted and added via a binary
		# 	search to improve speed.
		self.events = []

		pass

	def attach_observer(self, observer, area_idx: int):
		if area_idx is not None and area_idx >= self.no_areas:
			# TODO: raise Exception
			return False

		if area_idx is None or area_idx == -1:
			# attach to all areas 
			for i in range(0, self.no_areas):
				self.observers[i].append(observer)
			
			return True
			
		self.observers[area_idx].append(observer)
		return True

	def remove_observer(self, observer, area_idx: int):
		pass


	def _add_event_binary(self, event, start, end):
		"""
			Adds an event to the queue using binary search.
		"""
		if len(self.events) == 0:
			self.events.insert(0, event)
			return 0

		if start >= end:
			idx = end
			if self.events[start].time < event.time:
				idx = start + 1
			if self.events[end].time < event.time:
				idx = end + 1
			if idx < 0:
				idx = 0
			
			self.events.insert(idx, event)
			return start

		mid = floor((start + end) / 2)
		
		if self.events[mid].time > event.time:
			return self._add_event_binary(event, start, mid - 1)
		
		return self._add_event_binary(event, mid + 1, end)


	def add_event(self, event: Event):
		return self._add_event_binary(event, 0, len(self.events) - 1)
		
		pass

	def next_event(self):
		event = self.events.pop(0)
		self.now = event.time

		if self.now > self.stop_time:
			return False

		# notify all observers in that area
		if event.area_index in self.observers:
			for observer in self.observers[event.area_index]:
				observer(event)

		
		return event.time
	