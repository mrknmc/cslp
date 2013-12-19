# Bus Network Simulator

### Programming language
I picked Python as my programming language because it's nice. I have developed for version 2.7 since I am making use of some features only available from that version such as Counter from the collections library.
Python is probably my favourite language - I like its syntax. Also, since I had used it before I did not have to learn a new language for the practical which gave me more time to focus on the actual implementation. That being said, I would like to rewrite the practical in a functional language such as Haskell or OCaml one day.

### Changes from the version submitted on the first deadline
You may notice that I have changed quite a lot of code from the first deadline. I have decided to rewrite the way I compute all the possible events and the total rate. Instead of recomputing these every step of the simulation, I update them dynamically depending on the last chosen event.
This was kind of tricky since there are many possibilities for each event and I really hope I covered all of them. In the end it was actually quite fun and I am glad I did it. The profiling of this change is detailed in the Optimisations part below.

Furthermore, I now only allow passengers to board the first bus in the bus queue (as per the requirements) as opposed to all buses in the queue like in the first version.

I have also added support for analysis, experimentation, validation and optimisation as per the requirements.

### Running the simulator
To run the simulator on DiCE run `python2.7 run.py <inputfile>` in the simulator directory.

### Running the unit tests
Run any of the test files in the tests directory like so `python2.7 tests/models_tests.py`. Or run them all with a bash script `./tests/all`. The `update_tests.py` and `analysis_tests.py` are probably not really unit tests but they work pretty well.

### Optional arguments
You can supply the following arguments:
  1. input file (required) - `python2.7 run.py tests/test1` will take input from file tests/test1
  2. output file (optional) - `python2.7 run.py tests/test1 out.txt` will output to file out.txt

### Optimisations
Updating possible events dynamically has maybe decreased the maintainability and difficulty of the code but I have benchmarked both versions with the `time` command on `student.compute` and the results are pretty impressive. The average running times over 10 runs are listed in the table below:
<table>
<tr><th>Test file</th><th>New version</th><th>Old version</th><th>Speedup</th></tr>
<tr><td>test2</td><td>2.066</td><td>9.194</td><td>4.45x</td></tr>
<tr><td>test5</td><td>24.0.46</td><td>135.375</td><td>5.63x</td></tr>
<tr><td>test7</td><td>3.087</td><td>9.837</td><td>3.19x</td></tr>
</table>
As we can see the new running time is up to about 5 times faster than the old one. Given that I tried to properly document the code, I think this optimisation was very well worth it.

### Validation
Unit tests for validation are in the file `validation_tests.py`.

**Warnings**
I generate a warning on the following occasions since they don't affect the simulation in a harmful way:
  1. Road rate for two stops is specified but the road is not on any route.
  2. Road rate for two stops is specified but at least one of them is not on any route.
  3. Road rate for a stop to itself.

**Errors**
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

Some of these errors could be considered warnings, such as specifing a road rate twice (just use either one), but I think it's more beneficial to flag them as errors so the user of the system can fix them. I have also decided to not allow having a route with just one stop or having a route with the same stop twice in a row. Moreover, I am not allowing buses with 0 capacity, routes with 0 buses or stop time being 0.

### Conclusion
In conclusion, I thank you for this assignment - it was quite fun to finally do some actual coding. At first I was aiming for the early submission bus since I was working part-time and 3rd year is generally pretty busy I thought I'd rather do it properly than rush through it and make mistakes. Don't get me wrong, I still think that there are improvements I could make to my simulator (as always) but I think I definitely spent at least the recommended 100 hours on this.
