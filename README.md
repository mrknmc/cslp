# Bus Network Simulator

## Validation
Unit tests for validation are in the file `validation_tests.py`.
I have made the following assumptions while making the simulator:
  1. None of the rates can be smaller than 0. I did not see the point in running the simulation
  with any of the events disabled or having a road in the input with rate 0.
  2. Stop time has to be greater than 0. The output of such simulation would be empty. It seemed
  better to inform the user.
  3.


### Warnings
I generate a warning on the following occasions:
    1. Road rate for two stops is specified but the road is not on any route.
    2. Road rate for two stops is specified but at least one of them is not on any route.
    3. Road rate for a stop to itself.

### Errors
I generate an error on the following occasions:
    1. Road rate for a road that is on at least one route is not specified.
    2. Any of the rates is not specified.
    3. Stop time is not specified.
    4. Route has the same stop consecutively (twice in a row).
    5. Route has only one stop.
    6. Two routes with the same id are specified.
    7. Road rate is specified more than once.
    8. Stop time is specified more than once.
    9. Any of the event rates is specified more than once.
    10. Any of the event rates is zero.
    11. Stop time is zero
    12. Number of buses or capacity on any route is zero.

## Programming language
I picked Python as my programming language because it's nice.
I have developed for version 2.7 since I am making use of some features only available from that version such as Counter from the collections library.
I am comfortable with its syntax as I've used it before and I did not have to learn a new language for the practical.

### Running the simulator
To run the simulator on DiCE run `python2.7 run.py <inputfile>` in the simulator directory.

### Running the unit tests
Run any of the test files in the tests directory like so `python2.7 tests/models_tests.py`.

### Optional arguments
You can supply the following arguments arguments:
  1. input file (required) - `python2.7 run.py tests/test1` will take input from file tests/test1
  2. output file (optional) - `python2.7 run.py tests/test1 out.txt` will output to file out.txt
