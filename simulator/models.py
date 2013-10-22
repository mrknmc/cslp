from simulator.events import BusDeparture, BusArrival
from simulator.util import log
from simulator.errors import BusRoadStopConflict

from itertools import cycle
from collections import defaultdict


class Bus:

    def __init__(self, route, bus_id, capacity, stop, road):
        """
        Initialize a new bus. Set its current stop to the
        n-thstop of the route where n is the bus id.

        Also initialize the number of passengers to 0.
        """
        self.route = route
        self.bus_id = bus_id
        self.capacity = capacity
        self.passengers = []
        self.stop = stop
        self.road = road

    @property
    def uid(self):
        return '{0}.{1}'.format(self.route.route_id, self.bus_id)

    def can_satisfy(self, passenger):
        """
        Returns True if the bus can satisfy passenger's destination.
        """
        stop_ids = map(lambda s: s.stop_id, self.route.stops)
        return (passenger.destination in stop_ids)

    def board_passenger(self, passenger):
        """
        """
        self.passengers.append(passenger)

    def ready_for_departure(self):
        """
        Bus is ready for departure when it's not in motion, no one wants to disembark the bus
        and it has either full capacity or the bus stop has no passengers who want to board.
        """
        return (not self.in_motion) and \
               (self.full_capacity() or self.no_boarders()) and \
               self.no_disembarks()

    @property
    def in_motion(self):
        return self.road is not None

    def disembarking_passengers(self):
        """
        Return passengers that have arrived at their destination and want to disembark.
        """
        return (pax for pax in self.passengers if pax.destination == self.stop.stop_id)

    def full_capacity(self):
        """
        Returns true if the number of passengers is equal to the capacity.
        """
        if len(self.passengers) <= self.capacity:
            return len(self.passengers) == self.capacity
        raise Exception('More passengers than allowed!')

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
            self.stop.stop_id if self.stop else '-',
            '{0}-{1}'.format(self.road.origin, self.road.destination) if self.road else '-',
            len(self.passengers)
        )

    def __str__(self):
        return '{0}'.format(self.uid)


class Passenger:

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        # TODO: Below really should not be handled by the passenger
        # stop = network.get_stop(origin)
        # stop.enqueue_passenger(self)

    def __repr__(self):
        return 'Pax({0} - {1})'.format(self.origin, self.destination)


class Road:

    def __init__(self, origin, destination, rate):
        self.origin = origin
        self.destination = destination
        self.rate = rate

    def __repr__(self):
        return 'Road({0} - {1} | {2})'.format(self.origin, self.destination, self.rate)


class Route:

    def __init__(self, route_id, stops, bus_count, bus_capacity):
        self.route_id = route_id
        self.buses = []
        self.stops = stops

        # Create all the buses
        for bus_id, stop in zip(range(bus_count), cycle(stops)):
            bus = Bus(self, bus_id, bus_capacity, stop, None)
            stop.bus_queue.append(bus)
            self.buses.append(bus)

    def __repr__(self):
        return 'Route({0} | B: {1} | S: {2})'.format(self.route_id, len(self.buses), self.stop_ids)

    def __str__(self):
        return '{0}'.format(self.route_id)


class Stop:

    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.bus_queue = []
        self.passengers = []

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
            bus = self.bus_queue[0]  # catch errors here!
        return filter(bus.can_satisfy, self.passengers)

    def __repr__(self):
        return 'Stop({0} | B: {1} | P: {2})'.format(self.stop_id, self.bus_queue, self.passengers)

    def __str__(self):
        return str(self.stop_id)


class Network:
    """
    The object representing the bus network.
    """

    def __init__(self):
        """
        Represent everything using sets as there is no reason for duplicates.
        """
        # TODO: Maybe use matrix when dense and list when sparse?
        self.roads = defaultdict(set)
            # <stop_id> : {(<road>, )*}
        self.routes = {
            # <route_id> : <route>
        }
        self.stops = {
            # <stop_id> : <stop>
        }

    def get_route_by_id(self, route_id):
        """
        Return route given an id.
        """
        return self.routes[route_id]

    def add_route(self, route_id, stop_ids, bus_count, bus_capacity):
        """
        Create a new route and add it to the network. There is no need
        to create the stops since for a valid network there will always
        be roads specifying them.
        """
        stops = map(Stop, stop_ids)
        route = Route(route_id, stops, bus_count, bus_capacity)
        self.stops = dict(zip(stop_ids, stops))
        self.routes[route_id] = route

    def add_road(self, origin, destination, rate):
        """
        Create a new road, its stops and add it to the network.
        """
        road = Road(origin, destination, rate)
        self.roads[origin].add(road)

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
        """.format(roads=[list(r) for r in self.roads.values()], routes=self.routes.values())
