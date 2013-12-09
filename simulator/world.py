from random import choice, random
from math import log10
from models import Bus
from collections import Counter
from events import color_log as log, EventMap, PosCounter
from parser import parse_file
from collections import defaultdict
from itertools import product, izip, cycle


class World(object):

    def __init__(self, filename=None):
        """
        Initialize the world.
        """
        self.time = 0.0
        if not filename:
            return  # mainly for testing - init the world add params later
        network, rates, params, exps = parse_file(filename)
        self.network = network
        self.rates = rates
        self.experiments = exps
        # more efficient than PosCounter

        # Set all flags
        for key, val in params.iteritems():
            setattr(self, key, val)

    def initialise(self, caps=None, bus_counts=None):
        # Clear out the bus stops
        for stop in self.network.stops.itervalues():
            stop.bus_queue = []  # no buses on stops
            stop.wait_time = 0.0
            stop.pax_dests = PosCounter()  # no passengers on stops

        # Add all buses to stops
        for route in self.network.routes.itervalues():
            for bus_id, stop in izip(xrange(route.bus_count), cycle(route.stops)):
                bus = Bus(route, bus_id, stop)
                stop.bus_queue.append(bus)

        # Clear out the analysis dicts
        self.missed_pax = {'stops': Counter(), 'routes': Counter()}
        self.avg_pax = {'buses': defaultdict(lambda: (0, 0)), 'routes': defaultdict(lambda: (0, 0))}
        self.avg_busq = defaultdict(lambda: (0, 0))

        if bus_counts:
            # Update experimental bus counts
            for route_id, bus_count in bus_counts.iteritems():
                self.network.routes[route_id].bus_count = bus_count
        if caps:
            # Update experimental capacities
            for route_id, cap in caps.iteritems():
                self.network.routes[route_id].capacity = cap

        # Total rate starts as new_passengers which is always possible
        self.total_rate = self.rates['new_passengers']

        # Buses departing stops are the only possible events at the start
        self.event_map = EventMap()
        for stop in self.network.stops.itervalues():
            self.event_map.departs.extend(stop.bus_queue)
            self.total_rate += len(stop.bus_queue) * self.rates['departs']

    def dequeue_bus(self, bus):
        """
        The first bus departs from the queue.
        """
        cur_stop = bus.stop
        cur_stop.bus_queue.remove(bus)
        next_stop = bus.route.next_stop(cur_stop.stop_id)  # set next stop
        bus.road_rate = self.rates[cur_stop.stop_id, next_stop.stop_id]
        bus.stop = next_stop

    def record_missed_pax(self, bus):
        """"""
        if bus.full():
            for dest_id, count in bus.stop.pax_dests.iteritems():
                if bus.satisfies(dest_id):
                    self.missed_pax['routes'][bus.route.route_id] += count
                    self.missed_pax['stops'][bus.stop.stop_id] += count

    def record_pax_count(self, bus):
        bus_id = bus.bus_id
        route_id = bus.route.route_id
        bus_pax_sum = sum(bus.pax_dests.itervalues())

        # Update bus average
        count, avg = self.avg_pax['buses'][bus_id]
        new_avg = (count * avg + bus_pax_sum) / (count + 1.0)
        self.avg_pax['buses'][bus_id] = count + 1, new_avg

        # Update route average
        count, avg = self.avg_pax['routes'][route_id]
        new_avg = (count * avg + bus_pax_sum) / (count + 1.0)
        self.avg_pax['routes'][route_id] = count + 1, new_avg

    def record_bus_wait(self, stop):
        stop_id = stop.stop_id

        qing_count = len(stop.bus_queue[1:])
        count, summa = self.avg_busq[stop_id]
        self.avg_busq[stop_id] = count + 1, summa + qing_count * (self.time - stop.wait_time)

    def gen_pax(self):
        """
        Generates a passenger on the network.
        """
        orig = choice(self.network.stops.values())

        dests = []
        for route in self.network.routes.itervalues():
            try:
                idx = route.stops.index(orig)
                dests.extend(route.stops[:idx])
                dests.extend(route.stops[idx+1:])
            except ValueError:
                continue

        dest = choice(dests)
        return dict(orig=orig, dest=dest)

    def update(self, event_type, **kwargs):
        rates = self.rates
        total_rate = self.total_rate
        e_map = self.event_map

        if event_type == 'boards':
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
                    total_rate -= rates['boards']
                    e_map.boards[bus][dest_id] -= 1
                    # Bus may be ready for departure
                    if bus.departure_ready:
                        total_rate += rates['departs']
                        e_map.departs.append(bus)

            # The person can not board this bus
            total_rate -= rates['boards']
            e_map.boards[ebus][dest_id] -= 1

            # This bus could be ready for departure
            if ebus.departure_ready:
                total_rate += rates['departs']
                e_map.departs.append(ebus)

            # No one can board this bus anymore - it's full
            if ebus.full():
                bus_boards = sum(e_map.boards[ebus].itervalues())
                total_rate -= bus_boards * rates['boards']
                del(e_map.boards[ebus])

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
                total_rate += sum(bus_boards.itervalues()) * rates['boards']
                e_map.boards[bus] = bus_boards

            # If no one else wants to disembark or embark then it is departure ready
            if bus.departure_ready:
                total_rate += rates['departs']
                e_map.departs.append(bus)

        elif event_type == 'departs':
            bus = kwargs['bus']
            stop = bus.stop

            # Record passengers who couldn't get on
            self.record_missed_pax(bus)
            self.record_pax_count(bus)
            self.record_bus_wait(stop)

            stop.wait_time = self.time

            # Update the world
            self.dequeue_bus(bus)

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
                total_rate += sum(bus_boards.itervalues()) * rates['boards']
                e_map.boards[bus] = bus_boards
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
                    total_rate += rates['boards']
                    e_map.boards[bus][dest_id] += 1

    def choose_event(self):
        """
        Chooses an event based on the last event.
        """
        rand = random() * self.total_rate

        for bus, dest, count in self.event_map.gen_boards():
            rand -= count * self.rates['boards']
            if rand < 0:
                return 'boards', dict(dest=dest, bus=bus)

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
            self.boards is None,
            self.disembarks is None,
            self.departs is None,
            self.new_passengers is None,
            self.stop_time is None
        ]):
            raise Exception("The simulation is not valid.")
        self.network.validate()

    def log_stats(self):
        """This should maybe be done for all stops, routes and buses."""
        for route_id, count in self.missed_pax['routes'].iteritems():
            print('number of missed passengers route {0} {1}'.format(route_id, count))

        total = 0
        for stop_id, count in self.missed_pax['stops'].iteritems():
            total += count
            print('number of missed passengers stop {0} {1}'.format(stop_id, count))

        print('number of missed passengers {}\n'.format(total))

        for bus_id, (count, mean) in self.avg_pax['buses'].iteritems():
            print('average passengers bus {0} {1}'.format(bus_id, mean))

        total_count = total_avg = 0.0
        for route_id, (count, mean) in self.avg_pax['routes'].iteritems():
            total_count += 1
            total_avg += mean
            print('average passengers route {0} {1}'.format(route_id, mean))

        print('average passengers {}\n'.format(total_avg / total_count))

        total_count = total_sum = 0.0
        for stop_id, (count, summa) in self.avg_busq.iteritems():
            print count, summa
            total_count += count
            total_sum += summa
            print('average queueing at stop {0} {1}'.format(stop_id, summa / count))

        print('average queueing at all stops {}\n'.format(total_sum / total_count))

    def get_experiments(self, key):
        """
        """
        for comb in product(*self.experiments[key].itervalues()):
            yield dict(izip(self.experiments[key], comb))

    def experiment(self):
        """
        """
        bus_counts_gen = self.get_experiments('bus_count')
        for bus_counts in bus_counts_gen:
            caps_gen = self.get_experiments('cap')
            for caps in caps_gen:
                rates_gen = self.get_experiments('rates')
                for rates in rates_gen:
                    print bus_counts, caps, rates
                    self.rates.update(rates)
                    self.initialise(caps=caps, bus_counts=bus_counts)
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
