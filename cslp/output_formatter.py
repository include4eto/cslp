class OutputFormatter:
	"""
		Prints simulation output to stdout.
	"""
	TIME_FORMAT = "{0}:{1}:{2}:{3}"
	BIN_LOAD_CHANGES = "{0} -> load of bin {1}.{2} became {3:.3f} kg and contents volume {4:.3f} m^3"
	BIN_DISPOSAL = "{0} -> bag weighing {1:.3f} kg disposed of at bin {2}.{3}"
	BIN_OCCUPANCY_EXCEEDED = "{0} -> occupancy threshold of bin {1}.{2} exceeded"
	BIN_OVERFLOW = "{0} -> bin {1}.{2} overflowed"
	LORRY_DEPARTURE = "{0} -> lorry {1} left location {2}.{3}"
	LORRY_ARRIVAL = "{0} -> lorry {1} arrived at location {2}.{3}"
	LORRY_LOAD_CHANGES = "{0} -> load of lorry {1} became {2:.3f} kg and contents volume {3:.3f} m^3"

	def __init__(self, event_dispatcher):
		# define the main handler
		# 	attach to *all* areas
		event_dispatcher.attach_observer(self._on_event, None)
		self.enabled = True

	def _format_time(self, time):
		days = int(time / 86400)
		time = time % 86400

		hours = int(time / 3600)
		time = time % 3600

		minutes = int(time / 60)
		seconds = time % 60

		return OutputFormatter.TIME_FORMAT.format(
			str(days).zfill(2),
			str(hours).zfill(2),
			str(minutes).zfill(2),
			str(seconds).zfill(2)
		)

	def _on_event(self, event):
		if not self.enabled:
			return
		
		event_text = None
		time = self._format_time(event.time)

		if event.type == 'bin_load_changed':
			event_text = OutputFormatter.BIN_LOAD_CHANGES.format(
				time,
				event.area_index,
				event.data['bin_idx'],
				event.data['bin_weight'],
				event.data['bin_volume']
			)

		elif event.type == 'bin_disposal':
			event_text = OutputFormatter.BIN_DISPOSAL.format(
				time,
				event.data['bag_weight'],
				event.area_index,
				event.data['bin_idx']
			)
		elif event.type == 'bin_occupancy_exceeded':
			event_text = OutputFormatter.BIN_OCCUPANCY_EXCEEDED.format(
				time,
				event.area_index,
				event.data['bin_idx']
			)
		elif event.type == 'bin_overflow':
			event_text = OutputFormatter.BIN_OVERFLOW.format(
				time,
				event.area_index,
				event.data['bin_idx']
			)
		elif event.type == 'lorry_departure':
			event_text = OutputFormatter.LORRY_DEPARTURE.format(
				time,
				event.data['lorry_idx'],
				event.area_index,
				event.data['location']
			)
		elif event.type == 'lorry_arrival':
			event_text = OutputFormatter.LORRY_ARRIVAL.format(
				time,
				event.data['lorry_idx'],
				event.area_index,
				event.data['location']
			)
		elif event.type == 'lorry_load_changed':
			event_text = OutputFormatter.LORRY_LOAD_CHANGES.format(
				time,
				event.data['lorry_idx'],
				event.data['lorry_weight'],
				event.data['lorry_volume']
			)
		
		if event_text is not None:
			print(event_text)
		