import numpy as np

class StatisticsAggregator:
	def __init__(self, no_areas, event_dispatcher):
		# define the main handler
		# 	attach to *all* areas
		event_dispatcher.attach_observer(self._on_event, None)

		self.trips = [[] for x in range(no_areas)]
		self.trips_per_schedule = [[] for x in range(no_areas)]
		self.overflowed_bins = [[] for x in range(no_areas)]

		# need this if warm up time hasn't passed. in that case
		#	we could still get a trip event, but the trip will have
		# 	started before the warm up time and should not be accounted for here
		self.current_trip = [None] * no_areas

	def _on_event(self, event):

		if event.type == 'lorry_departure' and event.data.location == 0:
			# start of trip for the area
			trip = {
				'distance_travelled': 0,
				'weight_collected': 0,
				'volume_collected': 0,
				'start_time': event.time,
				'end_time': None
			}
			self.trips[event.area_index].append(trip)
			self.current_trip[event.area_index] = trip

			# this is a new trip for the current schedule
			self.trips_per_schedule[event.area_index][-1] += 1

		elif event.type == 'lorry_arrival':
			trip = self.current_trip[event.area_index]
			if trip is None:
				return
			
			trip['distance_travelled'] += event.data['distance_travelled']

			if event.data.location == 0:
				# end of trip
				trip['end_tipe'] = event.time
				self.current_trip[event.area_index] = None

		elif event.type == 'lorry_load_changed':
			trip = self.current_trip[event.area_index]
			if trip is None:
				return

			trip['volume_collected'] = event.data['lorry_volume']
			trip['weight_collected'] = event.data['lorry_weight']

		elif event.type == 'service_time':
			# append a new counter for the schedule
			self.trips_per_schedule[event.area_index].append(0)

		


		