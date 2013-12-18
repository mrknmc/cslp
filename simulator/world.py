from random import random, seed
from collections import defaultdict, Counter
from itertools import product, izip
from math import log10
from sys import maxint

from simulator.events import color_log as log, EventMap, PosCounter
from simulator.formats import ANALYSIS, EXPERIMENTS_PARAMS
from simulator.parser import parse_file


class World(object):
    """Controller object controlling the simulations."""

    def __init__(self, filename=None):
        self.time = 0.0
        if not filename:
            return  # mainly for testing - init the world add params later
        network, rates, params, exps = parse_file(filename)
        self.network = network
        self.rates = rates
        self.experiments = exps
        self.wtime = 0.0

        # Set all flags
        for key, val in params.iteritems():
            setattr(self, key, val)

    def initialise(self, rates=None, routes=None):
        """Initialise the world. Run before every experiment."""
        self.network.initialise()

        # Clear out the analysis dicts
        tuple_counter = lambda: defaultdict(lambda: (0, 0.0))
        self.analysis = {
            'missed_pax': {'stop': Counter(), 'route': Counter()},
            'avg_pax': tuple_counter(),
            'avg_qtime': Counter(),
            'avg_wtime': {'stop': Counter(), 'route': Counter()}
        }

        if rates:
            self.rates.update(rates)  # Update experimental rates

        if routes:
            # Update experimental bus counts and capacities
            for route_id, params in routes.iteritems():
                route = self.network.routes[route_id]
                route.bus_count = params.get('bus_count', route.bus_count)
                route.capacity = params.get('cap', route.capacity)

        # new passengers is always possible
        self.total_rate = self.rates['new_passengers']

        # Buses departing from stops are the only possible events at the start
        self.event_map = EventMap()
        for stop in self.network.stops.itervalues():
            self.event_map.departs.extend(stop.bus_queue)
            self.total_rate += len(stop.bus_queue) * self.rates['departs']

    def record_missed_pax(self, bus):
        """Update 'Number of Missed Passengers'.
        Done on per route and per stop basis."""
        for dest_id, count in bus.stop.pax_dests.iteritems():
            if bus.satisfies(dest_id):
                route_id = bus.route.route_id
                stop_id = bus.stop.stop_id
                self.analysis['missed_pax']['route'][route_id] += count
                self.analysis['missed_pax']['stop'][stop_id] += count

    def record_avg_pax(self, bus):
        """Update 'Average Passengers Per Bus Per Road'. Done on per bus basis
        only since we can reconstruct the route average from that."""
        bus_id = bus.bus_id
        bus_pax_sum = sum(bus.pax_dests.itervalues())

        count, summa = self.analysis['avg_pax'][bus_id]
        self.analysis['avg_pax'][bus_id] = count + 1, summa + bus_pax_sum

    def record_bus_wait(self, stop):
        """Update 'Average Bus Queuing Time'. Done on per stop basis."""
        qlength = stop.queue_length
        time_diff = self.time - stop.qtime
        self.analysis['avg_qtime'][stop.stop_id] += time_diff * qlength
        stop.qtime = self.time

    def record_pax_wait(self, bus=None, stop=None):
        """Update 'Average Waiting Passengers'.
        Done on per stop and per route basis."""
        if bus:
            stop = bus.stop
        pax_count = stop.pax_count
        stop_id = stop.stop_id
        time_diff = self.time - stop.wtime
        self.analysis['avg_wtime']['stop'][stop_id] += pax_count * time_diff
        stop.wtime = self.time

        time_diff = self.time - self.wtime
        for route_id, route in self.network.routes.iteritems():
            pax_count = sum(s.pax_count for s in route.stops)
            self.analysis['avg_wtime']['route'][route_id] += pax_count * time_diff

        self.wtime = self.time

    def update(self, event_type, bus=None, orig=None, dest=None):
        """Updates the world and the event map based
        on the last event and its parameters."""
        rates = self.rates
        e_map = self.event_map

        if event_type == 'board':
            self.record_pax_wait(bus=bus)

            bus.board(dest)  # Put the passenger on the bus

            # Other buses may be ready for departure now
            for other_bus in bus.stop.bus_queue[1:]:
                if other_bus.satisfies(dest) and not other_bus.full():
                    if other_bus.departure_ready:
                        self.total_rate += rates['departs']
                        e_map.departs.append(other_bus)

            # The person can not board this bus
            self.total_rate -= rates['board']
            e_map.board[bus][dest] -= 1

            # This bus could be ready for departure
            if bus.departure_ready:
                self.total_rate += rates['departs']
                e_map.departs.append(bus)

            if bus.full():
                # No one can board this bus anymore - it's full
                bus_boards = sum(e_map.board[bus].itervalues())
                self.total_rate -= bus_boards * rates['board']
                del(e_map.board[bus])

        elif event_type == 'disembarks':
            bus.disembark()  # Remove a passenger from the bus

            # Event not available anymore
            self.total_rate -= rates['disembarks']
            if bus.disembarks == 0:
                e_map.disembarks.remove(bus)

            # If the bus was full and it's the head then people can board it
            if bus.full(offset=1) and bus.is_head:
                bus_boards = PosCounter(dict(bus.boards))
                self.total_rate += sum(bus_boards.itervalues()) * rates['board']
                e_map.board[bus] = bus_boards

            # If no one wants to disembark or embark then it's departure ready
            if bus.departure_ready:
                self.total_rate += rates['departs']
                e_map.departs.append(bus)

        elif event_type == 'departs':
            # Record passengers who couldn't get on
            if bus.full():
                self.record_missed_pax(bus)
            self.record_avg_pax(bus)
            self.record_bus_wait(bus.stop)

            # Event is not available anymore
            self.total_rate -= rates['departs']
            e_map.departs.remove(bus)

            # If this was the head bus then the next bus can be boarded now
            if bus.is_head and len(bus.stop.bus_queue) >= 2:
                new_head = bus.stop.bus_queue[1]
                bus_boards = PosCounter(dict(new_head.boards))
                if bus_boards and not new_head.full():
                    # Some people want to board the bus
                    self.total_rate += sum(bus_boards.itervalues()) * rates['board']
                    e_map.board[new_head] = bus_boards

            # Update the world
            bus.dequeue(self.rates)

            # Bus is on the road now
            self.total_rate += bus.road_rate
            e_map.arrivals.append(bus)

        elif event_type == 'arrivals':
            # Record stop waiting time
            self.record_bus_wait(bus.stop)
            bus.stop.bus_count += 1

            # Event not available anymore
            e_map.arrivals.remove(bus)
            self.total_rate -= bus.road_rate

            # Update the world
            bus.arrive()

            # People on the stop can board the bus if it's not full and is head
            if bus.is_head and not bus.full():
                bus_boards = PosCounter(dict(bus.boards))
                if bus_boards:
                    # Some people want to board the bus
                    self.total_rate += sum(bus_boards.itervalues()) * rates['board']
                    e_map.board[bus] = bus_boards

            if bus.departure_ready:
                # No one wants to board the bus - it can depart
                self.total_rate += rates['departs']
                e_map.departs.append(bus)
            else:
                # People want to disembark the bus
                bus_disembarks = bus.disembarks
                self.total_rate += bus_disembarks * rates['disembarks']
                if bus_disembarks and bus not in e_map.disembarks:
                    e_map.disembarks.append(bus)
        else:
            self.record_pax_wait(stop=orig)

            # Update the world
            orig.pax_dests[dest.stop_id] += 1

            dest_id = dest.stop_id
            if orig.bus_queue:
                head = orig.bus_queue[0]

                if head.satisfies(dest_id) and not head.full():
                    # The person can board the head of the origin stop
                    self.total_rate += rates['board']
                    e_map.board[head][dest_id] += 1

                # Bus cannot depart now if it satisfies the destination
                for bus in orig.bus_queue:
                    if bus.satisfies(dest_id) and not bus.full():
                        if bus in e_map.departs:
                            self.total_rate -= rates['departs']
                            e_map.departs.remove(bus)

    def choose_event(self):
        """Chooses an event based on the rates and possible events."""
        rand = random() * self.total_rate

        for bus, dest, count in self.event_map.gen_board():
            rand -= count * self.rates['board']
            if rand < 0:
                return 'board', dict(dest=dest, bus=bus)

        for bus in self.event_map.disembarks:
            rand -= bus.disembarks * self.rates['disembarks']
            if rand < 0:
                return 'disembarks', dict(bus=bus)

        for bus in self.event_map.departs:
            rand -= self.rates['departs']
            if rand < 0:
                return 'departs', dict(dest=bus.stop, bus=bus)

        for bus in self.event_map.arrivals:
            rand -= bus.road_rate
            if rand < 0:
                return 'arrivals', dict(bus=bus)

        return 'new_passengers', self.network.generate_passenger()

    def sample_delay(self):
        """Return a delay sampled from an exponential distribution
        based on the total rate."""
        mean = 1 / self.total_rate
        return -mean * log10(random())

    def validate(self):
        """If any of the needed rates was not set the simulation is not valid.
        Next, validate the network.
        """
        if any([
            self.board is None,
            self.disembarks is None,
            self.departs is None,
            self.new_passengers is None,
            self.stop_time is None
        ]):
            raise Exception("The simulation is not valid.")
        self.network.validate()

    def log_stats(self):
        """Logging the summary statistics"""
        # Number of Missed Passengers
        total = 0
        for route_id in self.network.routes.iterkeys():
            count = self.analysis['missed_pax']['route'][route_id]
            total += count
            log_ans('missed_pax', 'route', route_id, count)

        for stop_id in self.network.stops.iterkeys():
            count = self.analysis['missed_pax']['stop'][stop_id]
            log_ans('missed_pax', 'stop', stop_id, count)

        log_ans('missed_pax', 'total', total)

        # Average Passengers Per Bus Per Road
        total_count = total_sum = 0.0
        for route_id, route in self.network.routes.iteritems():
            route_count = route_sum = 0
            for bus_no in xrange(route.bus_count):
                # construct bus_id dynamically because we don't
                # hold a reference to routes' buses
                bus_id = '{}.{}'.format(route_id, bus_no)
                count, summa = self.analysis['avg_pax'][bus_id]
                route_count += count
                route_sum += summa
                avg = 0 if summa == 0 else summa / count
                log_ans('avg_pax', 'bus', bus_id, avg)

            total_count += route_count
            total_sum += route_sum
            route_avg = 0 if route_sum == 0 else route_sum / route_count
            log_ans('avg_pax', 'route', route_id, route_avg)

        total_avg = 0 if total_sum == 0 else total_sum / total_count

        # Average Bus Queuing Time
        total_sum = total_count = 0.0
        for stop_id, stop in self.network.stops.iteritems():
            summa = self.analysis['avg_qtime'][stop_id]
            total_sum += summa
            total_count += stop.bus_count
            avg = 0 if summa == 0 else summa / stop.bus_count
            log_ans('avg_qtime', 'stop', stop_id,  avg)

        total_avg = 0 if total_sum == 0 else total_sum / total_count
        log_ans('avg_qtime', 'total', total_avg)

        # Average Waiting Passengers
        total_sum = 0.0
        for route_id in self.network.routes.iterkeys():
            summa = self.analysis['avg_wtime']['route'][route_id]
            total_sum += summa
            avg = 0 if summa == 0 else summa / self.stop_time
            log_ans('avg_wtime', 'route', route_id, avg)

        for stop_id in self.network.stops.iterkeys():
            summa = self.analysis['avg_wtime']['stop'][stop_id]
            avg = 0 if summa == 0 else summa / self.stop_time
            log_ans('avg_wtime', 'stop', stop_id, avg)

        total_avg = 0 if total_sum == 0 else total_sum / self.stop_time
        log_ans('avg_wtime', 'total', total_avg)

        print ('')

    def log_experiment(self, routes, rates):
        """Log the experimental parameters of routes and experimental rates."""
        for route_id, params in routes.iteritems():
            route = self.network.routes[route_id]
            print(EXPERIMENTS_PARAMS['route'].format(
                route_id=route_id,
                stops=' '.join(str(stop.stop_id) for stop in route.stops),
                bus_count=params.get('bus_count', route.bus_count),
                cap=params.get('cap', route.capacity)
            ))
        for name, rate in rates.iteritems():
            # tuple -> road, float -> normal rate
            name = EXPERIMENTS_PARAMS['road'].format(*name) if isinstance(name, tuple) else name
            print(EXPERIMENTS_PARAMS['rate'].format(name=name, rate=rate))

    def cleanup(self):
        """Run after every run of the simulation.
        Ensures that the analysis is correct."""
        for stop_id, stop in self.network.stops.iteritems():
            # Add remaining queueing buses to stops
            time_diff = self.stop_time - stop.qtime
            queueing_buses = stop.queue_length
            self.analysis['avg_qtime'][stop_id] += time_diff * queueing_buses
            # Add remamining waiting passengers to stops
            time_diff = self.stop_time - stop.wtime
            self.analysis['avg_wtime']['stop'][stop_id] += time_diff * stop.pax_count

        time_diff = self.stop_time - self.wtime
        # Add remamining waiting passengers to routes
        for route_id, route in self.network.routes.iteritems():
            pax_count = sum(s.pax_count for s in route.stops)
            self.analysis['avg_wtime']['route'][route_id] += time_diff * pax_count


    def experiment(self):
        """Run all experiments. If the optimise parameters flag is set,
        only print the most optimal one."""
        route_combs = {}
        # Get all combinations of capacities and bus counts within a route
        for route_id, comb in self.experiments['routes'].iteritems():
            route_combs[route_id] = (dict(izip(comb, x)) for x in product(*comb.itervalues()))

        combs = {}
        combs['routes'] = (dict(izip(route_combs, x)) for x in product(*route_combs.itervalues()))

        rates_combs = []
        # Get all combinations of all rates
        for comb in product(*self.experiments['rates'].itervalues()):
            rates_combs.append(dict(izip(self.experiments['rates'], comb)))

        if rates_combs:
            combs['rates'] = rates_combs

        # These variables determine the best set of parameters
        best_exp = None
        best_ans = None
        best_cost = maxint

        for exp_params in (dict(izip(combs, x)) for x in product(*combs.itervalues())):
            if not self.optimise:
                self.log_experiment(**exp_params)
            self.initialise(**exp_params)
            self.time = 0.0
            self.run(silent=True)
            self.cleanup()
            if not self.optimise:
                self.log_stats()
            else:
                cost = self.get_cost(exp_params)
                if cost < best_cost:
                    best_cost = cost
                    best_exp = dict(exp_params)
                    best_ans = dict(self.analysis)

        if self.optimise:
            self.log_experiment(**best_exp)
            self.analysis = best_ans
            self.log_stats()

    def start(self):
        """Validate and then start the run loop."""
        if self.experimental_mode:
            self.experiment()
        else:
            self.initialise()
            self.run()
            self.cleanup()
            self.log_stats()

    def run(self, silent=False):
        """
        Run the simulation until world explodes.
        """
        while self.time <= self.stop_time:
            delay = self.sample_delay()
            event_type, kwargs = self.choose_event()
            self.update(event_type, **kwargs)
            if not silent:
                log(event_type, time=self.time, **kwargs)
            self.time += delay

    def get_cost(self, exp_params):
        """Returns the total costs of given experiment parameters."""
        total_count = total_sum = 0.0
        for route_id, (count, summa) in self.analysis['avg_wtime']['route'].iteritems():
            total_count += count
            total_sum += summa

        params_sum = sum(rate for rate in exp_params['rates'].itervalues())

        for route in exp_params['routes'].itervalues():
            params_sum += route.get('cap', 0)
            params_sum += route.get('bus_count', 0)

        return params_sum * (total_sum / total_count)


def log_ans(ans_type, key, *args):
    print(ANALYSIS[ans_type][key].format(*args))
