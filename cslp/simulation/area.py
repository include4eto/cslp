from .disposal_modeling import DisposalModeling
from .event_dispatcher import Event
import numpy as np

class Area:
	LORRY_SERVICE_TIME_MODIFIER = 5

	def __init__(self, config, event_dispatcher, RoutePlanner):
		# di is the dependency injector, we use it to
		#	use the event dispatcher and the like
		self.config = config
		self.area_idx = self.config['areaIdx']

		# this is injected here at runtime
		self.event_dispatcher = event_dispatcher
		
		# initialize the lorry
		self.lorry = {
			'current_weight': 0,
			'current_volume': 0,
			# Whether the lorry is en route
			'busy': False,
			'current_route': None,
			# where in the route we are
			'route_index': 0,
			# if a service event fires when the lorry is busy
			#	this tells us we need to immediately reschedule
			'need_of_reschedule': False
		}

		# create all bins - they are simly a dictionary with
		# 	a capacity - that simple
		# NOTE: the index of the bin is the index in this array
		# NOTE: index 0 is not a bin, but an empty object (the depot)
		#	this will change once the bins are part of the area map
		self.bins = [None]
		for i in xrange(1, self.config['noBins'] + 1):
			self.bins.append({
				'idx': i,
				'current_volume': 0,
				'current_weight': 0,
				'has_overflowed': False,
				'has_exceeded_occupancy': False
			})

		# instantiate the injected route planner
		self.route_planner = RoutePlanner(area_map = self.config['roadsLayout'], \
			total_nodes = self.config['noBins'] + 1)
		
		# finally, attach an observer to repeat disposal events
		self.event_dispatcher.attach_observer(self._event_handler, self.area_idx)

		self.last_disposal = 0
		self.ylims = ''

	def reset(self, config):
		# TODO: document
		self.config = config

		for bin in self.bins[1:]:
			bin['current_volume'] = 0
			bin['current_weight'] = 0
			bin['has_overflowed'] = False
			bin['has_exceeded_occupancy'] = False

		self.lorry['current_weight'] = 0
		self.lorry['current_volume'] = 0
		self.lorry['route_index'] = 0
		self.lorry['busy'] = False
		self.lorry['current_route'] = None
		self.lorry['need_of_reschedule'] = False

	def init(self):
		self._init_disposal_events()
		
		# add first service interval
		service_time = int(round(60 * 60 / self.config['serviceFreq'], 3))
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now + service_time, self.area_idx, 'service_time')
		)

	def _init_disposal_events(self):
		for bin in self.bins:
			if bin is not None:
				self._schedule_next_disposal(bin)

	def _schedule_next_disposal(self, bin):
		# get the time to the next disposal event, in seconds
		time = DisposalModeling.inv_erlang_k(self.config['disposalDistrShape'],
			self.config['disposalDistrRate'])
		
		# round to three digits and convert from hours to seconds
		# TODO: maybe export there magic numbers somewhere?
		time = int(round(time * 60 * 60, 3))

		bag_weight = np.random.uniform(self.config['bagWeightMin'], self.config['bagWeightMax'])
		bag_weight = round(bag_weight, 3)

		self.event_dispatcher.add_event(
			# The event's data is the bin index & disposal volume
			Event(self.event_dispatcher.now + time, self.area_idx, 'bin_disposal', {
				'bin_idx': bin['idx'],
				'bag_vol': self.config['bagVolume'],
				'bag_weight': bag_weight
			})
		)

	def _on_bin_disposal(self, event):
		# add the garbage to the bin.. so to speak 
		bin_idx = event.data['bin_idx']
		bin = self.bins[bin_idx]
		
		if bin['has_overflowed']:
		# nothing should happen if the bin overflowed
			self._schedule_next_disposal(bin)
			return

		bin['current_volume'] = bin['current_volume'] + event.data['bag_vol']
		bin['current_weight'] = bin['current_weight'] + event.data['bag_weight']

		# calculate the occupancy
		occupancy = bin['current_volume'] / self.config['binVolume']
		occupancy = round(occupancy, 3)

		# this event will be reported by the output module
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now, self.area_idx, 'bin_load_changed', {
				'bin_idx': bin_idx,
				'bin_volume': bin['current_volume'],
				'bin_weight': bin['current_weight']
			})
		)

		if not bin['has_exceeded_occupancy'] and occupancy > self.config['thresholdVal']:
			# generate an occupancy exceeded event
			self.event_dispatcher.add_event(
				Event(self.event_dispatcher.now, self.area_idx, 'bin_occupancy_exceeded', {
					'bin_idx': bin_idx,
					'occupancy': occupancy
				})
			)

			bin['has_exceeded_occupancy'] = True

		if not bin['has_overflowed'] and occupancy > 1:
			# generate an overflow event
			self.event_dispatcher.add_event(
				Event(self.event_dispatcher.now, self.area_idx, 'bin_overflow', {
					'bin_idx': bin_idx,
					'occupancy': occupancy
				})
			)
			bin['has_overflowed'] = True
		
		# finally, generate the next disposal event
		self._schedule_next_disposal(bin)

	def _on_service_time(self, event, skip_service_event = False):
		if self.ylims is not None:
			self.ylims += 'line([{0} {0}], ylim);\n'.format(event.time)
		service_time = int(round(60 * 60 / self.config['serviceFreq'], 3))

		if not skip_service_event:
			self.event_dispatcher.add_event(
				Event(self.event_dispatcher.now + service_time, self.area_idx, 'service_time')
			)

			# emit number of overflowed bins, for statistics
			self.event_dispatcher.add_event(
				Event(self.event_dispatcher.now, self.area_idx, 'bins_overflowed_at_service_time', {
					'no_bins': len(filter(lambda bin: bin is not None and bin['has_overflowed'], self.bins))
				})
			)

		if self.lorry['busy']:
			# need to cascade this
			self.lorry['need_of_reschedule'] = True
			return False

		# calculate the lorry's route and start it off
		route = self.route_planner.get_route(self.bins[1:], flatten_route = True)
		if route == False:
			return
		
		self.lorry['current_route'] = route
		self.lorry['route_index'] = 0
		self.lorry['busy'] = True

		# emit dispatch event
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now, self.area_idx, 'lorry_departure', {
				'lorry_idx': 0,
				'location': 0
			})
		)

		# schedule arrival event
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now + route[0]['distance'] * 60, self.area_idx, 'lorry_arrival', {
				'lorry_idx': 0,
				'location': route[0]['target']
			})
		)

	def _on_lorry_available(self, event):
		# the lorry has now been emptied and is free
		self.lorry['current_route'] = None
		self.lorry['route_index'] = 0
		self.lorry['busy'] = False
		self.lorry['current_volume'] = 0
		self.lorry['current_weight'] = 0

		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now, self.area_idx, 'lorry_load_changed', {
				'lorry_idx': 0,
				'lorry_volume': 0,
				'lorry_weight': 0
			})
		)

		# cascaded rescheduling
		if self.lorry['need_of_reschedule']:
			self.lorry['need_of_reschedule'] = False
			self._on_service_time(None, skip_service_event = True)
			

	def _on_lorry_arrival(self, event):
		data = event.data
		if data['location'] == 0:
			self.event_dispatcher.add_event(
				Event(self.event_dispatcher.now, self.area_idx, 'trip_completed', {
					'lorry_idx': 0
				})
			)

			# When at depot we will consider the time required to empty a lorry is also fixed
			#	and this is five times as long as the bin service time.
			self.event_dispatcher.add_event(
				Event(self.event_dispatcher.now + Area.LORRY_SERVICE_TIME_MODIFIER * self.config['binServiceTime'],
					self.area_idx, 'lorry_available', {
					'lorry_idx': 0
				})
			)
			return
		
		bin_idx = data['location']
		bin = self.bins[bin_idx]

		# if we can't empty the current bin, we go to the depot
		if (self.config['lorryVolume'] < self.lorry['current_volume'] + bin['current_volume'] / 2.0) or \
			self.config['lorryMaxLoad'] < self.lorry['current_weight'] + bin['current_weight']:
			self._reschedule_trip_to_depot(bin_idx)

			return
		

		# NOTE: We empty the bin after the `binServiceTime`, if any bags are thrown in in the meantime,
		#	they are also collected
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now + self.config['binServiceTime'], self.area_idx, 'bin_emptied', {
				'lorry_idx': 0,
				'location': data['location']
			})
		)

	def _reschedule_trip_to_depot(self, bin_idx):
		# schedule a trip to the depot immediately and flag for reschedule
		self.lorry['need_of_reschedule'] = True
		route = self.route_planner.get_route_to_depot(bin_idx, flatten_route = True)
		self.lorry['current_route'] = route
		self.lorry['route_index'] = 0
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now, self.area_idx, 'lorry_departure', {
				'lorry_idx': 0,
				'location': bin_idx
			})
		)
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now + route[0]['distance'] * 60, self.area_idx, 'lorry_arrival', {
				'lorry_idx': 0,
				'location': route[0]['target']
			})
		)

	def _on_bin_emptied(self, event):
		data = event.data

		bin_idx = data['location']
		bin = self.bins[bin_idx]
		
		# NOTE: This solves an edge case where a bag is disposed of while
		#	the lorry is emptying the bin and that causes the lorry not to be
		#	able to service the bin.
		# NOTE (from specs): upon service a lorry compresses the contents of a bin to half its original volume
		if (self.config['lorryVolume'] < self.lorry['current_volume'] + bin['current_volume'] / 2.0) or \
			self.config['lorryMaxLoad'] < self.lorry['current_weight'] + bin['current_weight']:
			self._reschedule_trip_to_depot(bin_idx)

			return
			
		# otherwise proceed with emptying the bin
		self.lorry['current_volume'] += bin['current_volume'] / 2.0
		self.lorry['current_weight'] += bin['current_weight']
		bin['current_volume'] = 0
		bin['current_weight'] = 0
		bin['has_exceeded_occupancy'] = False
		bin['has_overflowed'] = False

		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now, self.area_idx, 'bin_load_changed', {
				'bin_idx': bin_idx,
				'bin_volume': bin['current_volume'],
				'bin_weight': bin['current_weight']
			})
		)
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now, self.area_idx, 'lorry_load_changed', {
				'lorry_idx': 0,
				'lorry_volume': self.lorry['current_volume'],
				'lorry_weight': self.lorry['current_weight']
			})
		)
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now, self.area_idx, 'lorry_departure', {
				'lorry_idx': 0,
				'location': bin_idx
			})
		)

		self.lorry['route_index'] += 1
		next_target = self.lorry['current_route'][self.lorry['route_index']]
		self.event_dispatcher.add_event(
			Event(self.event_dispatcher.now + next_target['distance'] * 60, self.area_idx, 'lorry_arrival', {
				'lorry_idx': 0,
				'location': next_target['target']
			})
		)

	def _event_handler(self, event):


		if event.time > 603800:
			if self.ylims is not None:
				print(self.ylims)
				self.ylims = None
		else:
			if event.time - self.last_disposal >= 10:
				self.last_disposal = event.time	
				weights = map(lambda bin: bin['current_volume'], self.bins[1:])
				
				average_occupancy = np.mean(weights)
				print('[{0} {1}]'.format(event.time, average_occupancy))

		if event.type == 'bin_disposal':
			self._on_bin_disposal(event)
		elif event.type == 'service_time':
			self._on_service_time(event)
		elif event.type == 'lorry_arrival':
			self._on_lorry_arrival(event)
		elif event.type == 'bin_emptied':
			self._on_bin_emptied(event)
		elif event.type == 'lorry_available':
			self._on_lorry_available(event)
