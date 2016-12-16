import numpy as np

class StatisticsAggregator:
	DELIMITER = "---"

	AREA_TRIP_DURATION = "area {0}: average trip duration {1}:{2}"
	OVERALL_TRIP_DURATION = "overall average trip duration {0}:{1}"

	AREA_NO_TRIPS = "area {0}: average no. trips {1:.3f}"
	OVERALL_NO_TRIPS = "overall average no. trips {0:.3f}"
	
	AREA_TRIP_EFFICIENCY = "area {0}: trip efficiency {1:.3f}"
	OVERALL_TRIP_EFFICIENCY = "overall trip efficiency {0:.3f}"
	
	AREA_VOL_COLLECTED = "area {0}: average volume collected {1:.3f}"
	OVERALL_VOL_COLLECTED = "overall average volume collected {0:.3f}"

	AREA_PERCENTAGE_BINS_OVERFLOWED = "area {0}: percentage of bins overflowed {1}"
	OVERALL_PERCENTAGE_BINS_OVERFLOWED = "overall percentage of bins overflowed {0}"

	def __init__(self, config, event_dispatcher):
		# define the main handler
		# 	attach to *all* areas
		event_dispatcher.attach_observer(self._on_event, None)
		self.config = config
		self.no_areas = config['noAreas']
		self.warm_up_time = config['warmUpTime'] * 60 * 60

		self.trips = [[] for x in range(self.no_areas)]
		self.trips_per_schedule = [[] for x in range(self.no_areas)]
		self.overflowed_bins = [[] for x in range(self.no_areas)]

		# need this if warm up time hasn't passed. in that case
		#	we could still get a trip event, but the trip will have
		# 	started before the warm up time and should not be accounted for here
		self.current_trip = [None] * self.no_areas

	def _on_event(self, event):
		if event.time <= self.warm_up_time:
			return

		if event.type == 'lorry_departure' and event.data['location'] == 0:
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

			if event.data['location'] == 0:
				# end of trip
				trip['end_time'] = event.time
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

		elif event.type == 'bins_overflowed_at_service_time':
			self.overflowed_bins[event.area_index].append(event.data['no_bins'])

	def print_output(self):
		print(StatisticsAggregator.DELIMITER)

		# total trips per all areas
		total_trips = 0

		# trip duration
		trip_duration_aggregate = 0
		for i in xrange(self.no_areas):
			# take the duration
			avg_min, avg_sec = '00', '00'
			if len(self.trips[i]) != 0:
				completed_trips = filter(lambda trip: trip['end_time'] is not None, self.trips[i])

				total_trips += len(completed_trips)

				trips = map(lambda trip: trip['end_time'] - trip['start_time'], completed_trips)
				avg = np.mean(trips)
				trip_duration_aggregate += np.sum(trips)

				avg_min, avg_sec = int(avg / 60), int(avg % 60)
				avg_min, avg_sec = str(avg_min).zfill(2), str(avg_sec).zfill(2)

			print(
				StatisticsAggregator.AREA_TRIP_DURATION.format(i, avg_min, avg_sec)
			)

		if total_trips > 0:
			trip_duration_aggregate /= float(total_trips)

		avg_min, avg_sec = int(trip_duration_aggregate / 60), int(trip_duration_aggregate % 60)
		avg_min, avg_sec = str(avg_min).zfill(2), str(avg_sec).zfill(2)
		print(
			StatisticsAggregator.OVERALL_TRIP_DURATION.format(avg_min, avg_sec)
		)

		# trips per schedule
		total_trips_per_schedule = 0
		total_schedules = 0
		for i in xrange(self.no_areas):
			avg_trips = 0
			if len(self.trips_per_schedule[i]) != 0:
				avg_trips = np.mean(self.trips_per_schedule[i])
				total_trips_per_schedule += np.sum(self.trips_per_schedule[i])

				total_schedules += len(self.trips_per_schedule[i])

			print(StatisticsAggregator.AREA_NO_TRIPS.format(i, avg_trips))

		if total_schedules > 0:
			total_trips_per_schedule /= float(total_schedules)
		print(StatisticsAggregator.OVERALL_NO_TRIPS.format(total_trips_per_schedule))

		# efficiency
		total_weight = 0
		total_time = 0
		for i in xrange(self.no_areas):
			efficiency = 0

			if len(self.trips[i]) != 0:
				completed_trips = filter(lambda trip: trip['end_time'] is not None, self.trips[i])
				weight = np.sum(map(lambda trip: trip['weight_collected'], completed_trips))
				time = np.sum(map(lambda trip: trip['end_time'] - trip['start_time'], completed_trips))
				
				efficiency = float(weight) / float(time)
				total_weight += weight
				total_time += time

			print(StatisticsAggregator.AREA_TRIP_EFFICIENCY.format(i, efficiency))

		total_efficiency = 0
		if total_time > 0:
			total_efficiency = float(total_weight) / float(total_time)
		print(StatisticsAggregator.OVERALL_TRIP_EFFICIENCY.format(total_efficiency))

		# volume collected
		total_vol = 0
		for i in xrange(self.no_areas):
			vol = 0

			if len(self.trips[i]) != 0:
				completed_trips = filter(lambda trip: trip['end_time'] is not None, self.trips[i])
				trips = map(lambda trip: trip['volume_collected'], completed_trips)
				vol = np.mean(trips)
				
				total_vol += np.sum(trips)
			
			print(StatisticsAggregator.AREA_VOL_COLLECTED.format(i, vol))

		if total_trips > 0:
			total_vol /= float(total_trips)
		print(StatisticsAggregator.OVERALL_VOL_COLLECTED.format(total_vol))
		

		# bins overflowed
		total_overflowed = 0
		for i in xrange(self.no_areas):
			overflowed = 0

			if len(self.overflowed_bins[i]) != 0:
				overflowed = np.mean(self.overflowed_bins[i])
				overflowed /= float(self.config['areas'][i]['noBins'])

				total_overflowed += np.sum(self.overflowed_bins[i]) / float(self.config['areas'][i]['noBins'])
			
			print(StatisticsAggregator.AREA_PERCENTAGE_BINS_OVERFLOWED.format(i, int(overflowed * 100)))
			
		if total_schedules > 0:
			total_overflowed /= float(total_schedules)
		print(StatisticsAggregator.OVERALL_PERCENTAGE_BINS_OVERFLOWED.format(int(total_overflowed * 100)))


		print(StatisticsAggregator.DELIMITER)
