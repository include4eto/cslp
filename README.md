# Computer Science Large Practical 2016-17
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
	|__ statistics: Statistics module, hooks up to the event dispatcher.

	|__ output_formatter.py: Generates output to the standard output stream, again
		uses the event dispatcher.
	|__ config.py: Contains the application config, such as usage information.
	|__ input_parser.py: Parses the input configuration.
	|__ app.py: main entry point, glues everything together

|__ test - Test root (see below for more detailed description)
```

## Pipeline
The input parser is the starting point of the application. Once we get a valid configuration file from the parser,
we instantiate the `Simulation` class, which is in charge of creating `Area` objects, which contain the actual simulation code.
In the future, experiments will simply be multiple `Simulation` classes with the appropriate configuration, perhaps wrapped
in an `Run` class. To glue things together, the `EventDispatcher` is injected in the constructor of the Simulation, which in turn
injects it into each area class. Statistics and output are achieved similarly. The `EventDispatcher` class is injected into an `OutputFormatter` and
later on, into a `Statistics` class. The same holds true for graphics, reports, etc.

The simple pipeline now looks like this:
```python
# create the parser
input_parser = InputParser(<input_file>)
input_parser.parse()

# check the parser results and exit if errors found

# create the event dispatcher
event_dispatcher = EventDispatcher(<options>)

# hook up an output formatter
output_formatter = OutputFormatter(<options>, dispatcher)

# create the simulation
simulation = Simulation(<config>, event_dispatcher)

# check for config validation errors and exit/output warnings if any

while True:
	current_time = dispatcher.next_event()

	# if current_time is False, the stop time has been reached
	if current_time == False:
		<exit application>
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

## `SimulationTest`
**currently unused**
