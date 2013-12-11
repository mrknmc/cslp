from random import choice, random
from collections import defaultdict, Counter
from itertools import product, izip, cycle
from math import log10
from sys import maxint

from simulator.models import Bus
from simulator.events import color_log as log, EventMap, PosCounter
from simulator.formats import ANALYSIS, EXPERIMENTS_PARAMS
from simulator.parser import parse_file


class World(object):

    def __init__(self, filename=None):
        self.time = 0.0
        if not filename:
            return  # mainly for testing - init the world add params later
        network, rates, params, exps = parse_file(filename)
        self.network = network
        self.rates = rates
        self.experiments = exps

        # Set all flags
        for key, val in params.iteritems():
            setattr(self, key, val)

    def initialise(self, rates=None, routes=None):
        """
        Initialise the world. Run before every experiment.
        """
        # Clear out the bus stops
        for stop in self.network.stops.itervalues():
            stop.bus_queue = []  # no buses on stops
            stop.wait_time = 0.0
            stop.pax_dests = PosCounter()  # no passengers on stops

        # Add all buses to stops
        for route in self.network.routes.itervalues():
            for bus_id, stop in izip(xrange(route.bus_count), cycle(route.stops)):
                bus = Bus(route, bus_id)
                stop.bus_queue.append(bus)

        # Clear out the analysis dicts
        tuple_counter = lambda: defaultdict(lambda: (0, 0.0))
        self.analysis = {
            'missed_pax': {'stop': Counter(), 'route': Counter()},
            'avg_pax': tuple_counter(),
            'avg_qtime': tuple_counter(),
            'avg_wtime': {'stop': tuple_counter(), 'route': tuple_counter()}
        }

        if rates:
            # Update experimental rates
            self.rates.update(rates)

        if routes:
            # Update experimental bus counts and capacities
            for route_id, params in routes.iteritems():
                route = self.network.routes[route_id]
                route.bus_count = params.get('bus_count', route.bus_count)
                route.capacity = params.get('cap', route.capacity)

        # Total rate starts as new_passengers which is always possible
        self.total_rate = self.rates['new_passengers']

        # Buses departing stops are the only possible events at the start
        self.event_map = EventMap()
        for stop in self.network.stops.itervalues():
            self.event_map.departs.extend(stop.bus_queue)
            self.total_rate += len(stop.bus_queue) * self.rates['departs']

    def record_missed_pax(self, bus):
        """
        Update 'Number of Missed Passengers'.
        Done on per route and per stop basis.
        """
        for dest_id, count in bus.stop.pax_dests.iteritems():
            if bus.satisfies(dest_id):
                self.analysis['missed_pax']['route'][bus.route.route_id] += count
                self.analysis['missed_pax']['stop'][bus.stop.stop_id] += count

    def record_avg_pax(self, bus):
        """
        Update 'Average Passengers Per Bus Per Road'.
        Done on per bus basis only since we can reconstruct route avg from that.
        """
        bus_id = bus.bus_id
        bus_pax_sum = sum(bus.pax_dests.itervalues())

        # Update bus average
        count, summa = self.analysis['avg_pax'][bus_id]
        self.analysis['avg_pax'][bus_id] = count + 1, summa + bus_pax_sum

    def record_bus_wait(self, stop):
        """
        Update 'Average Bus Queuing Time'.
        Done on per stop basis.
        """
        stop_id = stop.stop_id

        qing_count = len(stop.bus_queue[1:])
        count, summa = self.analysis['avg_qtime'][stop_id]
        self.analysis['avg_qtime'][stop_id] = count + 1, summa + qing_count * (self.time - stop.wait_time)

    def record_pax_wait(self):
        """
        Update 'Average Waiting Passengers'.
        Done on per stop and per route basis.
        """
        for stop in self.network.stops.itervalues():
            stop_id = stop.stop_id
            stop_pax_sum = sum(stop.pax_dests.itervalues())
            count, summa = self.analysis['avg_wtime']['stop'][stop_id]
            self.analysis['avg_wtime']['stop'][stop_id] = count + 1, summa + stop_pax_sum

        for route in self.network.routes.itervalues():
            route_id = route.route_id
            for stop in route.stops:
                stop_pax_sum = sum(stop.pax_dests.itervalues())
                count, summa = self.analysis['avg_wtime']['route'][route_id]
                self.analysis['avg_wtime']['route'][route_id] = count + 1, summa + stop_pax_sum

    def gen_pax(self):
        """
        Generates a passenger on the network.
        His destination stop must be satisfiable from his origin stop.
        """
        orig = choice(self.network.stops.values())

        dests = []
        for route in self.network.routes.itervalues():
            try:
                idx = route.stops.index(orig)
                dests.extend(route.stops[:idx])
                dests.extend(route.stops[idx+1:])
            except ValueError:
                # raised when the origin stop is not on this route
                continue

        dest = choice(dests)
        return dict(orig=orig, dest=dest)

    def update(self, event_type, **kwargs):
        """
        Updates the world and the event map based on the last event and its
        parameters.
        """
        rates = self.rates
        total_rate = self.total_rate
        e_map = self.event_map

        self.record_pax_wait()

        if event_type == 'board':
            ebus = kwargs['bus']
            dest_id = kwargs['dest']
            stop = ebus.stop

            # Update the world
            stop.pax_dests[dest_id] -= 1  # no longer on the stop
            ebus.pax_dests[dest_id] += 1  # now on the bus

            # The person can not board any other buses anymore
            for bus in stop.bus_queue:
                if bus == ebus:
                    continue  # skip the bus of this event
                if bus.satisfies(dest_id) and not bus.full():
                    total_rate -= rates['board']
                    e_map.board[bus][dest_id] -= 1
                    # Bus may be ready for departure
                    if bus.departure_ready:
                        total_rate += rates['departs']
                        e_map.departs.append(bus)

            # The person can not board this bus
            total_rate -= rates['board']
            e_map.board[ebus][dest_id] -= 1

            # This bus could be ready for departure
            if ebus.departure_ready:
                total_rate += rates['departs']
                e_map.departs.append(ebus)

            # No one can board this bus anymore - it's full
            if ebus.full():
                bus_boards = sum(e_map.board[ebus].itervalues())
                total_rate -= bus_boards * rates['board']
                del(e_map.board[ebus])

        elif event_type == 'disembarks':
            bus = kwargs['bus']
            stop_id = bus.stop.stop_id

            # Update the world
            bus.pax_dests[stop_id] -= 1  # no longer on the bus

            # Event not available anymore
            total_rate -= rates['disembarks']
            if bus.disembarks == 0:
                e_map.disembarks.remove(bus)

            # If the bus was full then people can now board it
            if bus.full(offset=1):
                bus_boards = PosCounter(dict(bus.boards))
                total_rate += sum(bus_boards.itervalues()) * rates['board']
                e_map.board[bus] = bus_boards

            # If no one else wants to disembark or embark then it is departure ready
            if bus.departure_ready:
                total_rate += rates['departs']
                e_map.departs.append(bus)

        elif event_type == 'departs':
            bus = kwargs['bus']
            stop = bus.stop

            # Record passengers who couldn't get on
            if bus.full():
                self.record_missed_pax(bus)
            self.record_avg_pax(bus)
            self.record_bus_wait(stop)

            stop.wait_time = self.time

            # Update the world
            bus.dequeue(self.rates)

            # Event is not available anymore
            total_rate -= rates['departs']
            e_map.departs.remove(bus)

            # How it affects other events
            total_rate += bus.road_rate
            e_map.arrivals.append(bus)

        elif event_type == 'arrivals':
            bus = kwargs['bus']
            stop = bus.stop
            road_rate = bus.road_rate

            # Record stop waiting time
            self.record_bus_wait(stop)

            stop.wait_time = self.time

            # Update the world
            stop.bus_queue.append(bus)  # on the stop now
            bus.road_rate = None  # no longer on the road

            # Event not available anymore
            e_map.arrivals.remove(bus)
            total_rate -= road_rate

            # People on the stop can now board the bus if it isnt full
            bus_boards = PosCounter(dict(bus.boards))
            if bus_boards and not bus.full():
                # Some people want to board the bus
                total_rate += sum(bus_boards.itervalues()) * rates['board']
                e_map.board[bus] = bus_boards
            elif bus.departure_ready:
                # No one wants to board the bus - it can depart
                total_rate += rates['departs']
                e_map.departs.append(bus)

            # People on the bus can now disembark it
            bus_disembarks = bus.disembarks
            # print bus_disembarks
            total_rate += bus_disembarks * rates['disembarks']
            if bus_disembarks and bus not in e_map.disembarks:
                e_map.disembarks.append(bus)
        else:
            # Update the world
            orig, dest = kwargs['orig'], kwargs['dest']
            orig.pax_dests[dest.stop_id] += 1

            # The person can board some buses on the origin stop
            dest_id = dest.stop_id
            for bus in orig.bus_queue:
                if bus.satisfies(dest_id) and not bus.full():
                    # Bus can not depart now if it satisfies the destination
                    if bus in e_map.departs:
                        total_rate -= rates['departs']
                        e_map.departs.remove(bus)
                    total_rate += rates['board']
                    e_map.board[bus][dest_id] += 1

    def choose_event(self):
        """
        Probabilistically chooses an event.
        """
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

        return 'new_passengers', self.gen_pax()

    def sample_delay(self):
        """
        Return a sample delay based on the total rate.
        """
        mean = 1 / self.total_rate
        return -mean * log10(random())

    def validate(self):
        """
        If any of the needed rates was not set the simulation is not valid.

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
        """
        Logging the summary statistics
        """
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
                # construct bus_id dynamically because we don't hold a reference to routes' buses
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
        log_ans('avg_pax', 'total', total_avg)

        # Average Bus Queuing Time
        total_count = total_sum = 0.0
        for stop_id in self.network.stops.iterkeys():
            count, summa = self.analysis['avg_qtime'][stop_id]
            total_count += count
            total_sum += summa
            avg = 0 if summa == 0 else summa / count
            log_ans('avg_qtime', 'stop', stop_id,  avg)

        total_avg = 0 if total_sum else total_sum / total_count
        log_ans('avg_qtime', 'total', total_avg)

        # Average Waiting Passengers
        total_count = total_sum = 0.0
        for route_id in self.network.routes.iterkeys():
            count, summa = self.analysis['avg_wtime']['route'][route_id]
            total_count += count
            total_sum += summa
            avg = 0 if summa == 0 else summa / count
            log_ans('avg_wtime', 'route', route_id, avg)

        for stop_id in self.network.stops.iterkeys():
            count, summa = self.analysis['avg_wtime']['stop'][stop_id]
            avg = 0 if summa == 0 else summa / count
            log_ans('avg_wtime', 'stop', stop_id, summa / count)

        total_avg = 0 if total_sum == 0 else total_sum / total_count
        log_ans('avg_wtime', 'total', total_sum / total_count)

        print ('')

    def get_experiments(self, key):
        """
        """
        for comb in product(*self.experiments[key].itervalues()):
            yield dict(izip(self.experiments[key], comb))

    def log_experiment(self, routes, rates):
        """
        Log the experimental parameters of routes and experimental rates.
        """
        for route_id, params in routes.iteritems():
            route = self.network.routes[route_id]
            print(EXPERIMENTS_PARAMS['route'].format(
                route_id=route_id,
                stops=' '.join(map(lambda s: str(s.stop_id), route.stops)),
                bus_count=params.get('bus_count', route.bus_count),
                cap=params.get('cap', route.capacity)
            ))
        for name, rate in rates.iteritems():
            # tuple -> road, float -> normal rate
            name = EXPERIMENTS_PARAMS['road'].format(*name) if isinstance(name, tuple) else name
            print(EXPERIMENTS_PARAMS['rate'].format(name=name, rate=rate))

    def experiment(self):
        """
        TODO: give some proper names to the fancy generators
        and variables in this method.
        """
        combs = {}
        for route_id, comb in self.experiments['routes'].iteritems():
            combs[route_id] = [dict(izip(comb, x)) for x in product(*comb.itervalues())]

        mombs = {}

        mombs['routes'] = (dict(izip(combs, x)) for x in product(*combs.itervalues()))

        rates_gen = list(self.get_experiments('rates'))
        if rates_gen:
            mombs['rates'] = rates_gen

        for a in (dict(izip(mombs, x)) for x in product(*mombs.itervalues())):
            self.log_experiment(**a)
            self.initialise(**a)
            self.time = 0.0
            self.run(silent=True)
            self.log_stats()

    def start(self):
        """
        Validate and then start the run loop.
        """
        if self.experimental_mode:
            self.experiment()
        else:
            self.initialise()
            self.run()

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


def log_ans(ans_type, key, *args):
    print(ANALYSIS[ans_type][key].format(*args))
