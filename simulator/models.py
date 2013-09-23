from simulator.events import BusDeparture, BusArrival
from simulator.util import log

from collections import defaultdict


class Bus:

    def __init__(self, route_id, bus_id, capacity, stop_id):
        """
        Initialize a new bus. Set its current stop to the
        n-thstop of the route where n is the bus id.

        Also initialize the number of passengers to 0.
        """
        self.uid = "{0}.{1}".format(route_id, bus_id)
        self.capacity = int(capacity)
        self.passengers = []
        self.stop_id = stop_id
        self.in_motion = False

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
               (self.full_capacity() or self.stop.no_boarders()) and \
               self.no_disembarks()

    def ready_for_arrival(self):
        """
        Bus is ready for arrival when it's in motion.
        """
        pass

    def disembarking_passengers(self):
        """
        Return passengers that have arrived at their destination and want to disembark.
        """
        return [pax for pax in self.passengers if pax.destination == self.stop_id]

    def full_capacity(self):
        """
        Returns true if the number of passengers is equal to the capacity.
        """
        if len(self.passengers) <= self.capacity:
            return len(self.passengers) == self.capacity
        raise Exception('More passengers than allowed!')

    def no_disembarks(self):
        """
        Returns true if there are no passengers who want to disembark at the current bus stop.
        """
        # return filter(lambda p: p.destination == self.stop, self.passengers) == []
        return self.disembarking_passengers() == []

    def __repr__(self):
        return self.uid


class Passenger:

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        # TODO: Below really should not be handled by the passenger
        # stop = network.get_stop(origin)
        # stop.enqueue_passenger(self)


class Road:

    def __init__(self, origin, destination, rate):
        self.origin = origin
        self.destination = destination
        self.rate = rate


class Route:

    def __init__(self, route_id, stop_ids, bus_count, bus_capacity):
        self.route_id = route_id
        self.buses = []
        self.stop_ids = stop_ids

        for bus_id in range(bus_count):
            stop_id = stop_ids[bus_id]
            bus = Bus(route_id, bus_id, bus_capacity, stop_id)
            self.buses.append(bus)

    def __repr__(self):
        return self.route_id


class Stop:

    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.bus_queue = []
        self.passengers = []

    def enqueue_bus(self, bus):
        """
        A new bus arrives to the queue.
        """
        self.bus_queue.append(bus)
        event = BusArrival(bus, self)
        log(event)

    def dequeue_bus(self):
        """
        The first bus departs from the queue.
        """
        bus = self.bus_queue.pop(0)
        event = BusDeparture(bus, self)
        log(event)

    def enqueue_passenger(self, passenger):
        """
        A new passenger has arrived at the stop.
        """
        self.passengers.append(passenger)
        # MAYBE log the passenger creation event here?

    def __repr__(self):
        return self.stop_id


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
        route = Route(route_id, stop_ids, bus_count, bus_capacity)
        self.routes[route_id] = route

    def add_road(self, origin, destination, rate):
        """
        Create a new road, its stops and add it to the network.
        """
        # road = Road(origin, destination, rate)
        self.roads[origin].add((destination, rate))

    def validate(self):
        """
        Catch errors such as road not added for a route.
        Catch warnings such as road added but there is no route for it.
        This should be ran before the simulation.

        There could be more buses than there are stops.

        """
        pass
