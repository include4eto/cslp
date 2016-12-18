import numpy as np
from Queue import PriorityQueue

# TODO:
#  Possible configuration
# 	- greedy coeficient -> pick up bins that don't need servicing
# 	- caching?

class DijkstraRoutePlanner:
	CACHE_ENABLED = True
	CACHE_MAX_SIZE = 30000000
	CACHE_KEY = '{0}:{1}'

	DYNAMIC_BINS_THRESHOLD = 100

	ALGORITHM_GREEDY = 'greedy'
	ALGORITHM_PRIORITY = 'priority'
	ALGORITHM_DYNAMIC = 'dynamic'

	ALGORITHM = 'dynamic'

	def __init__(self, area_map, total_nodes, lorry_capacity = None, threshold_val = None):
		self.area_map = area_map
		self.total_nodes = total_nodes
		self.lorry_capacity = lorry_capacity
		self.threshold_val = threshold_val
		
		# path cache between sources
		#	path_cache[i] contains all routes from [i] to 
		#	path_cache[i]['target']
		self.path_cache = {}
		pass

	def _dijkstra(self, source, target, N, adj_list, service_target = True, flatten_route = False):
		# TODO: service bins that need servicing that you pass through
		if flatten_route and DijkstraRoutePlanner.CACHE_ENABLED:
			cache_key = DijkstraRoutePlanner.CACHE_KEY.format(source, target)
			if cache_key in self.path_cache:
				return self.path_cache[cache_key]

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
			'service': service_target,
			'distance': dist[target]
		})

		# we need not return the entire path
		if not flatten_route:
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

		target_path = target_path[::-1]

		if flatten_route and DijkstraRoutePlanner.CACHE_ENABLED:
			cache_size = len(self.path_cache)
			
			if cache_size <= DijkstraRoutePlanner.CACHE_MAX_SIZE:
				self.path_cache[cache_key] = target_path

		return target_path

	# NOTE: from here: https://piazza.com/class/ishzpr235bh5ox?cid=30
	# To save memory, you do not need to store all intermediary steps and
	#	 output events at intermediary locations. However, this may be 
	#	useful to you for checking that your implementation works as expected.
	def _get_route_greedy(self, bins, flatten_route=False):
		if len(bins) == 0:
			return False

		# sort the above by occupancy
		bins = sorted(bins, key = lambda x: x['current_volume'], reverse=True)
		
		# start at the depot
		current_location = 0
		final_path = []
		for b in bins:
			
			path = self._dijkstra(current_location, b['idx'], self.total_nodes, self.area_map, flatten_route = flatten_route)
			current_location = b['idx']
			
			final_path += path

		# the last part is getting to the depot
		final_path += self.get_route_to_depot(current_location, flatten_route = flatten_route)

		return final_path

	def _get_route_priority(self, bins, flatten_route=False):
		if len(bins) == 0:
			return False

		# start at the depot
		current_location = 0
		final_path = []

		# while there are bins to service
		while len(bins) != 0:
			# find the closest bin that needs servicing
			bin_paths = []
			for b_2 in bins:
				path = self._dijkstra(current_location, b_2['idx'], self.total_nodes, self.area_map, flatten_route = flatten_route)
				bin_paths.append((path[-1]['distance'], b_2['idx'], path))

			# sort the paths
			bin_paths = sorted(bin_paths, key = lambda x: x[0])

			# take the smallest
			target_path = bin_paths[0]
			bins = filter(lambda bin: bin['idx'] != target_path[1], bins)

			# and service it
			path = target_path[2]
			current_location = target_path[1]
			
			final_path += path

		# the last part is getting to the depot
		final_path += self.get_route_to_depot(current_location, flatten_route = flatten_route)

		return final_path

	def get_route(self, bins, flatten_route=False):
		# get only the bins that need servicing
		bins = filter(lambda x: x['has_exceeded_occupancy'], bins)

		if DijkstraRoutePlanner.ALGORITHM == DijkstraRoutePlanner.ALGORITHM_GREEDY:
			return self._get_route_greedy(bins, flatten_route)
		elif DijkstraRoutePlanner.ALGORITHM == DijkstraRoutePlanner.ALGORITHM_PRIORITY:
			return self._get_route_priority(bins, flatten_route)
		elif DijkstraRoutePlanner.ALGORITHM == DijkstraRoutePlanner.ALGORITHM_DYNAMIC:
			l = len(bins)
			if l > DijkstraRoutePlanner.DYNAMIC_BINS_THRESHOLD:
				return self._get_route_greedy(bins, flatten_route)
			else:
				return self._get_route_priority(bins, flatten_route)
		else:
			return self._get_route_greedy(bins, flatten_route)
			

	def get_route_to_depot(self, source, include_source = False, flatten_route = False):
		# don't service the depot'
		path = self._dijkstra(source, 0, self.total_nodes, self.area_map, service_target = False, flatten_route = flatten_route)

		if include_source:
			path.insert(0, {
				'target': source,
				'service': False
			})

		return path