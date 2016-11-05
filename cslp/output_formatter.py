class OutputFormatter:
	TIME_FORMAT = "{0}:{1}:{2}:{3}"
	BIN_LOAD_CHANGES = "{0} -> load of bin {1}.{2} became {3:.3f} kg and contents volume {4:.3f} mˆ3"
	BIN_DISPOSAL = "{0} -> bag weighing {1:.3f} kg disposed of at bin {2}.{3}"
	BIN_OCCUPANCY_EXCEEDED = "{0} -> occupancy threshold of bin {1}.{2} exceeded"
	BIN_OVERFLOW = "{0} -> bin {1}.{2} overflowed"

	def __init__(self, event_dispatcher):
		# define the main handler
		# 	attach to *all* areas
		event_dispatcher.attach_observer(self._on_event, None)

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
		
		if event_text is not None:
			print(event_text)