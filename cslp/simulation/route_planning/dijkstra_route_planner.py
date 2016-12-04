import numpy as np
from Queue import PriorityQueue

# TODO:
#  Possible configuration
# 	- greedy coeficient -> pick up bins that don't need servicing
# 	- caching?

class DijkstraRoutePlanner:
	# Factor governining greediness. Pick up bins that haven't overflowed
	# 	or exceeded threshold capacity, but are above this much of the
	# 	original threshold
	# TODO: use
	THRESHOLD_NON_OVERFLOWING = 0.5
	# TODO: use
	CACHE_ENABLED = True

	def __init__(self, area_map, total_bins, lorry_capacity, threshold_val):
		self.area_map = area_map
		self.total_bins = total_bins
		self.lorry_capacity = lorry_capacity
		self.threshold_val = threshold_val
		
		# path cache between sources
		#	path_cache[i] contains all routes from [i] to 
		#	path_cache[i]['target']
		self.path_cache = []
		pass

	@staticmethod
	def _dijkstra(source, target, N, adj_list, service_target = True):
		q = PriorityQueue()
		# we don't visit nodes twice
		visited = [False] * N
		visited[source] = True
		
		# path[i] = the note we reached i from
		path = [None] * N
		path[source] = source

		# the best found distance yet
		dist = [1 << 30] * N
		dist[source] = 0

		# start at the source
		q.put((0, source))

		while not q.empty():
			_, current = q.get()
			c_i = current
			c_d = dist[c_i]

			if c_i == target:
				break
			
			visited[c_i] = True

			for neighbor in adj_list[c_i]:
				n_i = neighbor['index']
				n_d = neighbor['path_length']
				
				# if the path is better, update it and push the item
				#	in the queue with the distance as a priority
				if (not visited[n_i]) and (dist[c_i] + n_d < dist[n_i]):
					dist[n_i] = dist[c_i] + n_d
					path[n_i] = c_i

					q.put((dist[n_i], n_i))

		# backtrack to find the actual path
		target_path = []
		i = target
		target_path.append({
			'target': target,
			'service': service_target
		})
		while True:
			i = path[i]

			if i == source or i is None:
				break
			target_path.append({
				'target': i,
				'service': False
			})
		# NOTE: we do not append the source to the path,
		#	since these are then concatenated

		return target_path[::-1]

	def get_route(self, bins):
		# get only the bins that need servicing
		bins = filter(lambda x: x['has_exceeded_occupancy'], bins)
		
		if len(bins) == 0:
			return False

		# sort the above by occupancy
		bins = sorted(bins, key = lambda x: x['current_volume'], reverse=True)
		
		# start at the depot
		current_location = 0
		final_path = [{
			'target': 0,
			'service': False
		}]
		for b in bins:
			
			path = DijkstraRoutePlanner._dijkstra(current_location, b['idx'], self.total_bins, self.area_map)
			current_location = b['idx']
			
			final_path += path

		# the last part is getting to the depot
		final_path += self.get_route_to_depot(current_location)

		return final_path

	def get_route_to_depot(self, source, include_source = False):
		# don't service the depot'
		path = DijkstraRoutePlanner._dijkstra(source, 0, self.total_bins, self.area_map, service_target = False)

		if include_source:
			path.insert(0, {
				'target': source,
				'service': False
			})

		return path