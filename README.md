# Computer Science Large Practical 2016-17

## Deadlines & Assessment
* [Part 1](https://bitbucket.org/patras/cslp-16-17/src/ff82b37587aee6436c06e953332292500354615d/part1_assessment.txt?at=master&fileviewer=file-view-default): Friday 7th October, 2016 at 16:00; zero-weigthed (for feedback only).
* [Part 2](https://bitbucket.org/patras/cslp-16-17/src/79c1bda2c12360554bb9249ed5e6dbca37a1a730/part2_assessment.txt?at=master&fileviewer=file-view-default): Friday 11th November, 2016 at 16:00; worth 50% of the marks.
* [Part 3](https://bitbucket.org/patras/cslp-16-17/src/79c1bda2c12360554bb9249ed5e6dbca37a1a730/part3_assessment.txt?at=master&fileviewer=file-view-default): Wednesday 21st December, 2016 at 16:00; worth 50% of the marks.

## Scoreboard
Your code will be automatically tested on a weekly basis and you will be able to keep track of your progress to a scoreboard soon to be linked here.

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
		|__ area.py: Simulation main for a single area
		|__ simulation.py: Wrapper for the simulation.
	|__ statistics: Statistics module, hooks up to the event dispatcher.
	|__ output: Generates output to the standard output stream, again
	|	uses the event dispatcher.
	
	|__ event.py: An event in the event dispatcher
	|__ event_dispatcher.py: Main event module, sorts
		and dispatches events
	|__ input_parser.py: Parses the input configuration.
	|__ app.py: main entry point, connects everything together
```