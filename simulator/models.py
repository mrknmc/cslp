from events import BusDeparture, BusArrival
from util import log


class Bus:

    def __init__(self, route_id, bus_id, capacity, stop_id):
        """
        Initialize a new bus. Set its current stop to the
        n-thstop of the route where n is the bus id.

        Also initialize the number of passengers to 0.
        """
        self.route_id = int(route_id)
        self.bus_id = int(bus_id)
        self.capacity = int(capacity)
        self.passengers = []
        self.next_stop = stop_id

    def __repr__(self):
        return '{0}.{1}'.format(self.route_id, self.bus_id)


# class Passenger:
    # pass


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
        self.queue = []

    def enqueue(self, bus):
        """
        A new bus arrives to the queue
        """
        self.queue.append(bus)
        event = BusArrival(bus, self)
        log(event)

    def dequeue(self):
        """
        The first bus departs from the queue
        """
        bus = self.queue.pop(0)
        event = BusDeparture(bus, self)
        log(event)

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
        self.roads = {
            # <stop_id> : [(<stop_id>, <rate>), *]
            # 1: [(2, 0.6), (3, 0.4)],
        }
        self.routes = {
            # <route_id> : {
                # "buses": [<bus>, *],
                # "stops": [<stop_id>, *],
                # "capacity": <capacity>
            # }
        }
        self.routes = {
            # <route_id> : [<stop_id>, *]
            # 2: [3, 5, 9],
        }

    def add_route(self, route_id, stop_ids, bus_count, bus_capacity):
        """
        Create a new route and add it to the network. There is no need
        to create the stops since for a valid network there will always
        be roads specifying them.
        """
        # route = Route(route_id, stop_ids, bus_count, bus_capacity)
        self.routes[route_id] = stop_ids

    def add_road(self, origin, destination, rate):
        """
        Create a new road, its stops and add it to the network.
        """
        # road = Road(origin, destination, rate)
        self.roads[origin] = destination, rate

    def validate(self):
        """
        Catch errors such as road not added for a route.
        Catch warnings such as road added but there is no route for it.
        This should be ran before the simulation.

        There could be more buses than there are stops.

        """
        pass
