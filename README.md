# Computer Science Large Practical 2016-17
This a bin collection simulator written in Python. The full specifications are available
under `/doc/cslp-2016-17.pdf`. A corresponding report outlining the work in detail is available
under `/doc/report.pdf`.

**NOTE: Miscellaneous notes at the end of this document**
## Command line parameters
- `-a, --algorithm`: Algorithm to use. One of greedy, priority, synamic
- `-dc, --disable-cache`: Disable/enable the algorithm cache
- `-cs, --cache-size`: Set the cache size
- `-b, --benchmark`: Display the runtime of the app
- `-d, --disable-output`: Disable all output except for statistics
- `-o, --benchmark-only`: Run only the benchmark and disable all other output
- `-dt, --dynamic-threshold`: Dynamic algorithm threshold

## Code Structure
### File Structure
The file structure follows the one outlined here [https://github.com/kennethreitz/samplemod](https://github.com/kennethreitz/samplemod).
In essence, we have one module `cslp`, which is in the folder `cslp`. All the tests are in the folder `test`, all relative to the project
root. In the `cslp` module we have the different parts of the project. See below:

```
cslp_root
| 	simulate.sh - Simulation start
| 	test.sh - Starts all testing suites
| 	compile.sh - Does nothing, since python needs no compilation
|
|___cslp - Module root folder
	|__ simulation: Simulation module, this is where the simulation and
		all the algrotithmic code is/
		|__ area.py: Simulation controller for a single area
		|__ simulation.py: Wrapper for the entire simulation.
		|__ disposal_modeling.py: Contains the logic for disposal delays.
		|__ event_dispatcher.py: Main events module, sorts
			and dispatches events
		|__ route_planning - Route planning algorithm
			|__ dijkstra_route_planner.py - Dijkstra route planner
	|__ statistics: Statistics module, hooks up to the event dispatcher.
		|__ statistics_aggregator.py - statistics module
	|__ output_formatter.py: Generates output to the standard output stream, again
		uses the event dispatcher.
	|__ config.py: Contains the application config, such as usage information.
	|__ input_parser.py: Parses the input configuration.
	|__ experiment_manager.py - Runtime experiment wrapper
	|__ app.py: main entry point, glues everything together

|__ test - Test root (see below for more detailed description)
|__ doc - Documentation and project reports
|__ statistics_plots - Code for producing statistics plots 
```

## Pipeline
The input parser is the starting point of the application. Once we get a valid configuration file from the parser,
we instantiate the `ExperimentManager`  class, which computer a grid of all experiments and creates a 
`Simulation`, which is in charge of creating `Area` objects, which contain the actual simulation code.
 To glue things together, the `EventDispatcher` is injected in the constructor of the Simulation, which in turn
injects it into each area class. Statistics and output are achieved similarly. The `EventDispatcher` class is injected into an `OutputFormatter` and
later on, into a `StatisticsAggregator` class. The route planning algorithm is injected in the `Area` class.

The simple pipeline now looks like this:
```python
# create the parser
input_parser = InputParser(<input_file>)
input_parser.parse()

# create the experiment manager
experiment_manager = ExperimentManager(config, disable_output=disable_output, disable_statistics=disable_statistics)

# run the experiments
experiment_manager.run_all()
```

### Error detection
The `InputParser` only detects parse errors. It does not check for unrealistic data,
since it's semantically wrong for those to be detected there. Instead, the `Simulation` class
will check for values that might be wrong (but correctly formatted). Therefore, those should also
be outputted, as in the pipeline above.

### Event dispatcher
The `EventDispatcher` class is a generic priority queue type object that can support one simulation.
Many `Observers`, in our case plain old python `functions` will be attached to it, filtered by area index.
It will run the simulation as long as `next_event` is called, until the `stop_time` is reached. It will
continuously call the attached observers when events happen. Note that observers can be attached to listen
to more than one area (as it's the case for the `OutputFormatter` and later, `Statistics`).

```python
def event_handler(event):
	# this will be called when events happen
	pass

event_dispatcher.attach_observer(event_handler)
```

## Testing
The application is tested using `pyunit`, glued together by `nose`. All tests are in the
`test` directory under the project root. Each test suite is in a file with suffix test (`<name>_test`).
The directory `inputs` contains input test files, specifically for input parser testing.

To run *all* tests, use `sh test.sh`. This uses `nose` with an `--exe` flag to support non-unix filesystems,
such as *ntfs*.

Within each test suite, each test case is labeled `test_<component>`. Currently, the following tests are performed:

Note all tests are white box, i.e. we assume we know how the code works.

### `InputParserTest` (`input_parser_test.py`):
- `test_valid_input`: Test to see a valid input is parsed and the correct configuration
		is returned.
- `test_invalid_input`: Tests a basic invalid file.
- `test_grid_input`: Tests with one big area grid.
- `test_valid_manu`: Tests that an input with many areas is correctly parsed.
- `test_invalid_rads`: Tests that an invalid roads layout is not accepted.
- `test_experimentation`: Tests that experimentation directives are parsed.
- `test_magnitude_viloation`: Tests to see attributes with correct formatting,
	but wrong magnitudes are detected.
- `test_extra_parameters`: Tests that extra parameters are treated as errors.
- `test_invalid_matrix`: Tests that matrices are checked for 0 entries apart from the
	diagonal.
- `test_max_magnitude`: Tests that values with the maximum magnitude are accepted.
- `test_whitespaces`: Tests that extra whitespaces are stripped.

### `AreaTest` (`area_test.py`):
- `test_observer_subscription`: Tests that areas attach an observer to the event
	dispatcher on startup.
- `test_initial_disposal_events`: Tests that areas generate initial disposal
	events correctly.
- `test_disposal_generation`: Tests that new disposal events are generated after
	disposals happen.
- `test_overflow`: Tests that overflow events are generated correctly.
- `test_occupancy_exceeded`: Tests that occupancy excess events are generated.

### `EventDispatcherTest` (`event_dispatcher_test.py`)
- `test_event_sorting`: Tests that events are always sorted correctly (in ascending order).
- `test_basic_observer`: Tests that observers are called when events happen.

### `OutputFormatterTest` (`output_formatter_test.py`)
- `test_time_formatting`: Tests that time in seconds is converted correctly to time in DD:HH:MM:SS
- `test_bin_output_events`: Tests that bin output events (bag disposed, load changed, occupancy exceeded & overflow)
	are outputted correctly to stdout.

### `DijkstraRoutePlannerTest` (`dijkstra_route_planner_test.py`)
- `test_basic`: Tests the greedy algorithm
- `test_priority_planner`: Tests the priority algorithm

### `StatisticsAggregatorTest` (`statistics_aggregator_test.py`)
- `test_trip_duration` - Tests the statistics aggregator test

### `SimulationTest`
**currently unused**

## Misc notes
- Areas can appear in shuffled order, as long as all are specified. I.e. this is valid:
	```
	areaIdx 1 ...
	...
	areaIdx 0 ...
	...
	```
- Outputs for some test files are stored in `test/outputs`

### Used objects structure
This is useful for visualizing what objects used in the simulation look like (that don't already
have a class).

#### Road adjacency list
```python
'roadsLayout': [
	[
		{ 'index': 0, 'path_length': 0 },
		{ 'index': 1, 'path_length': 3 },
		{ 'index': 5, 'path_length': 4 }
	],
	[
		...
	],
	...
]
```

#### Single bin
```python
{
	'idx': i,
	'current_volume': 0,
	'current_weight': 0,
	'has_overflowed': False,
	'has_exceeded_occupancy': False
}
```

#### Lorry paths
```python
[
	{ 'target': 5, 'delay': 2, 'service': True },
	{ 'target': 2, 'delay': 3, 'service': False },
	...
]
```

#### Lorry
```python
{
	'current_weight': 0,
	'current_volume': 0,
	# Whether the lorry is en route
	'busy': False,
	'current_route': None,
	'route_index': 0,
	# if a service event fires when the lorry is busy
	#	this tells us we need to immediately reschedule
	'need_of_reschedule': False
}
```