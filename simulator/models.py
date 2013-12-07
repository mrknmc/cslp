from itertools import cycle, izip, ifilter
from collections import Counter


class Bus(object):

    def __init__(self, route, bus_id, capacity, stop):
        """
        Initialize a new bus. Set its current stop to the
        n-thstop of the route where n is the bus id.

        Also initialize the number of passengers to 0.
        """
        self.route = route
        self.bus_id = '{}.{}'.format(route.route_id, bus_id)
        self.capacity = capacity
        self.pax_dests = Counter()
        self.stop = stop
        self.road_rate = None

    @property
    def in_motion(self):
        return self.road_rate is not None

    @property
    def departure_ready(self):
        """
        Bus is ready for departure when:
            - it's not in motion
            - no one wants to disembark the bus
            - it has either full capacity or no passengers want to board.
        """
        return (
            not self.in_motion and
            (self.full() or list(self.boards) == []) and
            self.disembarks == 0
        )

    @property
    def disembarks(self):
        """
        Return passengers that have arrived at their destination and want to disembark.
        """
        return self.pax_dests[self.stop.stop_id]

    @property
    def boards(self):
        """
        Return passengers that would like to board this bus.
        """
        # TODO: maybe get all stops from route and then dict-access them
        return ifilter(lambda i: self.satisfies(i[0]) and i[1] != 0, self.stop.pax_dests.iteritems())

    def full(self, offset=0):
        """
        Returns true if the bus is full.
        """
        return sum(self.pax_dests.itervalues()) + offset == self.capacity

    def satisfies(self, dest):
        """
        Returns True if the bus can satisfy passenger's destination.
        """
        return dest in (stop.stop_id for stop in self.route.stops)

    def __repr__(self):
        return 'Bus({0} | C: {1} | S: {2} | R: {3} | P: {4})'.format(
            self.bus_id,
            self.capacity,
            self.stop.stop_id,
            self.road_rate if self.road_rate else '-',
            sum(self.pax_dests.itervalues())
        )

    def __str__(self):
        return self.bus_id


class Route(object):

    def __init__(self, route_id, stops, bus_count, cap):
        self.route_id = route_id
        self.stops = stops

        # Create all the buses
        for bus_id, stop in izip(xrange(bus_count), cycle(stops)):
            bus = Bus(self, bus_id, cap, stop)
            stop.bus_queue.append(bus)

    def next_stop(self, stop_id):
        """
        Returns the next bus stop on this route for a stop_id.
        """
        next_idx = next(idx for idx, stop in enumerate(self.stops) if stop.stop_id == stop_id) + 1
        return self.stops[next_idx % len(self.stops)]

    def __repr__(self):
        stop_ids = ', '.join([str(stop.stop_id) for stop in self.stops])
        return 'Route({0} | S: {1})'.format(self.route_id, stop_ids)

    def __str__(self):
        return '{0}'.format(self.route_id)


class Stop(object):

    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.bus_queue = []
        self.pax_dests = Counter()

    def __repr__(self):
        return 'Stop({0} | B: {1} | P: {2})'.format(
            self.stop_id,
            self.bus_queue,
            sum(self.pax_dests.itervalues())
        )

    def __str__(self):
        return str(self.stop_id)


class Network(object):
    """
    The object representing the bus network.
    """

    def __init__(self):
        """
        Represent everything using sets as there is no reason for duplicates.
        """
        # TODO: Maybe use matrix when dense and list when sparse?
        self.routes = {
            # <route_id> : <route>
        }
        self.stops = {
            # <stop_id> : <stop>
        }

    def add_route(self, route_id, stop_ids, bus_count, cap):
        """
        Create a new route and add it to the network. There is no need
        to create the stops since for a valid network there will always
        be roads specifying them.
        """
        stops = map(Stop, stop_ids)
        route = Route(route_id, stops, bus_count, cap)
        self.stops = dict(izip(stop_ids, stops))
        self.routes[route_id] = route

    def validate(self):
        """
        Catch errors such as road not added for a route.
        Catch warnings such as road added but there is no route for it.
        This should be ran before the simulation.

        There could be more buses than there are stops.

        This could probably solved by representing the network as a graph
        and validating the graph.

        """
        pass

    def __repr__(self):
        """
        """
        return """
Routes: {routes}
Stops: {stops}
        """.format(routes=self.routes.values(), stops=self.stops.values())
