from itertools import cycle, chain, izip
from random import choice

from simulator.events import PosCounter
from simulator.formats import RATES_RX
from simulator.errors import InputError, InputWarning

class Bus(object):
    """Model representing a bus object of the simulation."""

    def __init__(self, route, bus_id):
        self.route = route
        self.bus_id = '{}.{}'.format(route.route_id, bus_id)
        self.pax_dests = PosCounter()
        self._cur_stop = bus_id % len(route.stops)
        self.road_rate = None

    @property
    def in_motion(self):
        """The bus is in motion if it has some road_rate assigned."""
        return self.road_rate is not None

    @property
    def stop(self):
        """Stop of this bus is accessed from the stops of the route."""
        return self.route.stops[self._cur_stop]

    @property
    def departure_ready(self):
        """
        Bus is ready for departure when:
            - no one wants to disembark the bus
            - it has either full capacity or no passengers want to board.
        """
        return self.disembarks == 0 and (self.full() or list(self.boards) == [])

    @property
    def is_head(self):
        """True if the bus is the head of its bus stop's bus queue."""
        return self == self.stop.bus_queue[0]

    @property
    def disembarks(self):
        """Number of passengers who want to disembark at the current stop."""
        return self.pax_dests[self.stop.stop_id]

    @property
    def boards(self):
        """Destination, count pairs of passengers from the current stop that would
        like to board this bus. Only bus at the front of the queue can be boarded.
        Only yield counts greater than 0."""
        for stop in self.route.stops:
            stop_id = stop.stop_id
            count = self.stop.pax_dests[stop_id]
            if count > 0:
                yield stop_id, count
        # return ifilter(lambda i: self.satisfies(i[0]) and i[1] != 0, self.stop.pax_dests.iteritems())

    @property
    def next_stop(self):
        """Next stop of this bus on its route.
        Loops to the first stop after the last one."""
        stops = self.route.stops
        try:
            return stops[self._cur_stop + 1]
        except IndexError:
            return stops[0]

    def board(self, dest):
        """Board a passenger with destination dest."""
        self.pax_dests[dest] += 1
        self.stop.pax_dests[dest] -= 1

    def disembark(self):
        """Disembark one passenger at the current stop."""
        self.pax_dests[self.stop.stop_id] -= 1

    def arrive(self):
        """Arrive to the current stop. We need to set road_rate to None."""
        self.stop.bus_queue.append(self)
        self.road_rate = None

    def full(self, offset=0):
        """Returns true if the bus is full. The optional offset argument is added
        to the current number of passengers, e.g.:
        count = 39, offset = 1, capacity = 40 -> bus is full"""
        return sum(self.pax_dests.itervalues()) + offset == self.route.capacity

    def satisfies(self, dest):
        """Checks if the destination is on this bus's route."""
        return dest in (stop.stop_id for stop in self.route.stops)

    def dequeue(self, rates):
        """Departs the bus from its stop.
        Also sets the road_rate and the stop to the next stop on the route."""
        self.stop.bus_queue.remove(self)
        next_stop = self.next_stop  # set next stop
        self.road_rate = rates[self.stop.stop_id, next_stop.stop_id]
        self._cur_stop = (self._cur_stop + 1) % len(self.route.stops)

    def __repr__(self):
        return 'Bus({0} | C: {1} | S: {2} | R: {3} | P: {4})'.format(
            self.bus_id,
            self.route.capacity,
            self.stop.stop_id,
            self.road_rate if self.road_rate else '-',
            sum(self.pax_dests.itervalues())
        )

    def __str__(self):
        return self.bus_id


class Route(object):
    """Model representing a route object of the simulation."""

    def __init__(self, route_id, stops, bus_count, capacity):
        self.route_id = route_id
        self.stops = stops
        self.bus_count = bus_count
        self.capacity = capacity

    def __repr__(self):
        stop_ids = ', '.join([str(stop.stop_id) for stop in self.stops])
        return 'Route({0} | S: {1})'.format(self.route_id, stop_ids)

    def __str__(self):
        return '{0}'.format(self.route_id)


class Stop(object):
    """Model representing a stop object of the simulation."""

    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.bus_queue = []
        self.pax_dests = PosCounter()
        self.qtime = 0.0
        self.wtime = 0.0

    @property
    def queue_length(self):
        """Returns the number of buses that are queueing (not head)."""
        return max(len(self.bus_queue) - 1, 0)

    def __repr__(self):
        return 'Stop({0} | P: {2} | B: {1})'.format(
            self.stop_id,
            self.bus_queue,
            sum(self.pax_dests.itervalues())
        )

    def __str__(self):
        return str(self.stop_id)


class Network(object):
    """Model representing a network object of the simulation."""

    def __init__(self):
        """Represent everything using sets as there is no reason for duplicates."""
        self.routes = {}  # <route_id> : <route>
        self.stops = {}  # <stop_id> : <stop>

    def initialise(self):
        """Initialise the network. Clear out all the bus stops from buses and
        passengers and add buses to stops."""
        for stop in self.stops.itervalues():
            stop.bus_queue = []
            stop.qtime = 0.0
            stop.pax_dests = PosCounter()

        for route in self.routes.itervalues():
            for bus_id, stop in izip(xrange(route.bus_count), cycle(route.stops)):
                bus = Bus(route, bus_id)
                stop.bus_queue.append(bus)

    def add_route(self, route_id, stop_ids, bus_count, cap, **kwargs):
        """Create a new route and add it to the network. Create a stop if it
        doesn't already exist. Also add references to stops to the route."""
        stops = []
        for stop_id in stop_ids:
            if stop_id in self.stops:
                stop = self.stops[stop_id]
            else:
                stop = Stop(stop_id)
                self.stops[stop_id] = stop
            stops.append(stop)
        self.routes[route_id] = Route(route_id, stops, bus_count, cap)

    def generate_passenger(self):
        """Generates a passenger on the network.
        His destination stop must be satisfiable from his origin stop."""
        orig = choice(self.stops.values())

        dests = []
        for route in self.routes.itervalues():
            try:
                idx = route.stops.index(orig)
                dests.extend(route.stops[:idx])
                dests.extend(route.stops[idx+1:])
            except ValueError:
                # raised when the origin stop is not on this route
                continue

        dest = choice(dests)
        return dict(orig=orig, dest=dest)

    def validate(self, rates, params):
        """
        Catch errors such as road not added for a route.
        Catch warnings such as road added but there is no route for it.
        This should be ran before the simulation.

        There could be more buses than there are stops.

        This could probably solved by representing the network as a graph
        and validating the graph.
        """
        for route in self.routes.itervalues():
            stop_ids = [stop.stop_id for stop in route.stops]
            first_last = (stop_ids[-1], stop_ids[0])
            for orig, dest in chain(izip(stop_ids, stop_ids[1:]), [first_last]):
                try:
                    rates[orig, dest]
                except KeyError:
                    raise InputError('Road from {} to {} is missing a rate.'.format(orig, dest))

        for rate_name in RATES_RX:
            try:
                rates[rate_name]
            except KeyError:
                raise InputError('Rate {} is missing from the input.'.format(rate_name))

        if 'stop_time' not in params:
            raise InputError('Stop time is missing from the input.'.format(rate_name))


    def __repr__(self):
        return """
Routes: {routes}
Stops: {stops}
        """.format(routes=self.routes.values(), stops=self.stops.values())
