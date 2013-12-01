from util import log

from itertools import cycle, izip, repeat
from collections import defaultdict


class Bus(object):

    def __init__(self, route, bus_id, capacity, stop, road_rate):
        """
        Initialize a new bus. Set its current stop to the
        n-thstop of the route where n is the bus id.

        Also initialize the number of passengers to 0.
        """
        self.route = route
        self.bus_id = bus_id
        self.capacity = capacity
        self.pax_dests = defaultdict(int)
        self.stop = stop
        self.road_rate = road_rate

    @property
    def uid(self):
        return '{0}.{1}'.format(self.route.route_id, self.bus_id)

    @property
    def in_motion(self):
        return self.road_rate is not None

    def can_satisfy(self, dest):
        """
        Returns True if the bus can satisfy passenger's destination.
        """
        return dest in (stop.stop_id for stop in self.route.stops)

    def ready_for_departure(self):
        """
        Bus is ready for departure when it's not in motion, no one wants to disembark the bus
        and it has either full capacity or the bus stop has no passengers who want to board.
        """
        return (not self.in_motion) and \
               (self.full_capacity() or self.no_boarders()) and \
               self.no_disembarks()

    def disembarking_passengers(self):
        """
        Return passengers that have arrived at their destination and want to disembark.
        """
        for pax, bus in izip(self.passengers, repeat(self)):
            if pax.dest == self.stop.stop_id:
                yield pax, bus

    def full_capacity(self):
        """
        Returns true if the number of passengers is equal to the capacity.
        """
        return len(self.passengers) == self.capacity

    def no_boarders(self):
        """
        Returns true if there are no passengers who want to board at the current bus stop.
        """
        return list(self.stop.boarding_passengers(bus=self)) == []

    def no_disembarks(self):
        """
        Returns true if there are no passengers who want to disembark at the current bus stop.
        """
        return list(self.disembarking_passengers()) == []

    def __repr__(self):
        return 'Bus({0} | C: {1} | S: {2} | R: {3} | P: {4})'.format(
            self.uid,
            self.capacity,
            self.stop.stop_id,
            self.road_rate if self.road_rate else '-',
            sum(self.pax_dests.itervalues())
        )

    def __str__(self):
        return '{0}'.format(self.uid)


class Route(object):

    def __init__(self, route_id, stops, bus_count, bus_capacity):
        self.route_id = route_id
        self.buses = []
        self.stops = stops

        # Create all the buses
        for bus_id, stop in zip(range(bus_count), cycle(stops)):
            bus = Bus(self, bus_id, bus_capacity, stop, None)
            stop.bus_queue.append(bus)
            self.buses.append(bus)

    def get_next_stop(self, stop_id):
        """
        Returns the next bus stop on this route for a stop_id.
        """
        next_idx = next(idx for idx, stop in enumerate(self.stops) if stop.stop_id == stop_id) + 1
        return self.stops[next_idx % len(self.stops)]

    def __repr__(self):
        return 'Route({0} | B: {1} | S: {2})'.format(self.route_id, len(self.buses), self.stop_ids)

    def __str__(self):
        return '{0}'.format(self.route_id)


class Stop(object):

    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.bus_queue = []
        self.pax_dests = defaultdict(int)

    def departing_buses(self):
        """
        Returns all the buses ready for departure.
        """
        return filter(Bus.ready_for_departure, self.bus_queue)

    def boarding_passengers(self, bus=None):
        """
        Returns all the passengers ready to board.
        """
        if not bus:
            for bus in self.bus_queue:
                for pax in self.passengers:
                    if bus.can_satisfy(pax):
                        yield pax, bus
        else:
            for pax in self.passengers:
                if bus.can_satisfy(pax):
                    yield pax, bus

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
        self.roads = {
            # <stop_id, stop_id> : rate
        }
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
        self.stops = dict(zip(stop_ids, stops))
        self.routes[route_id] = route

    def add_road(self, orig, dest, rate):
        """
        Create a new road, its stops and add it to the network.
        """
        self.roads[orig, dest] = rate

    def get_buses(self):
        """
        Returns all the buses in the network.
        """
        for route in self.routes.itervalues():
            for bus in route.buses:
                yield bus

    def get_stops(self):
        """
        Returns all the stops in the network.
        """
        for stop in self.stops.itervalues():
            yield stop

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
Roads: {roads}

Routes: {routes}
        """.format(roads=[list(r) for r in self.roads], routes=self.routes.values())
