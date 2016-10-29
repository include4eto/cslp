# TODO: remove this
import pprint
from .disposal_modeling import DisposalModeling
from .event_dispatcher import Event
import numpy as np

class Area:
	def __init__(self, config, event_dispatcher):
		# di is the dependency injector, we use it to
		#	use the event dispatcher and the like
		self.config = config
		self.area_idx = self.config['areaIdx']

		# this is injected here at runtime
		self.event_dispatcher = event_dispatcher
		
		# create all bins - they are simly a dictionary with
		# 	a capacity - that simple
		# NOTE: the index of the bin is the index in this array
		self.bins = []
		for i in range(0, self.config['noBins']):
			self.bins.append({
				'idx': i,
				'current_volume': 0,
				'current_weight': 0,
				'has_overflowed': False,
				'has_exceeded_occupancy': False
			})

		# pprint.pprint(self.config)
		
	def init_disposal_events(self):
		for bin in self.bins:
			self._schedule_next_disposal(bin)

		# finally, attach an observer to repeat disposal events
		self.event_dispatcher.attach_observer(self._event_handler, self.area_idx)

	def _schedule_next_disposal(self, bin):
		# get the time to the next disposal event, in seconds
		time = DisposalModeling.inv_erlang_k(self.config['disposalDistrRate'],
			self.config['disposalDistrShape'])
		
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
		
		# if bin['current_volume'] >= self.config['binVolume']:
		# 	# nothing should happen if the bin overflowed
		# 	self._schedule_next_disposal(bin)
		# 	return

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

	def _event_handler(self, event):
		if event.type == 'bin_disposal':
			self._on_bin_disposal(event)
