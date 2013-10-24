# Bus Network Simulator

## Programming language
I picked Python as my programming language because it's nice. I used version 2.6.8 because that is the one DiCE machines have.

## Current state
Right now, the simulator should work on valid input files. That is, it does not do any sort of validation.

### Running the simulator
To run the simulator just run `python run.py` in the simulator directory.

### Running the unit tests
Run any of the test files in the tests directory like so `python tests/models_tests.py`.

### Optional arguments
You can supply the following arguments arguments:
  1. input file (required) - `python run.py tests/test1` will take input from file tests/test1
  2. output file (optional) - `python run.py tests/test1 out.txt` will output to file out.txt
