from itertools import cycle, islice

from simulator.events import PosCounter
from simulator.formats import RATES_NAMES
from simulator.errors import InputError, InputWarning

class Bus(object):

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
        return self.route.stops[self._cur_stop]

    @property
    def departure_ready(self):
        """
        Bus is ready for departure when:
            - no one wants to disembark the bus
            - it has either full capacity or no passengers want to board.
        """
        return (self.full() or list(self.boards) == []) and self.disembarks == 0

    @property
    def disembarks(self):
        """
        Number of passengers who want to disembark at the current stop.
        """
        stop_id = self.stop.stop_id
        return self.pax_dests[stop_id]

    @property
    def boards(self):
        """
        Destination, count of passengers pairs from the current stop that would
        like to board this bus. Only yield counts greater than 0.
        """
        for stop in self.route.stops:
            stop_id = stop.stop_id
            count = self.stop.pax_dests[stop_id]
            if count > 0:
                yield stop_id, count
        # return ifilter(lambda i: self.satisfies(i[0]) and i[1] != 0, self.stop.pax_dests.iteritems())

    @property
    def next_stop(self):
        """
        Next stop of this bus on its route.
        """
        stops = self.route.stops
        if self._cur_stop == len(stops) - 1:
            return stops[0]

        return stops[self._cur_stop + 1]

    def full(self, offset=0):
        """
        Returns true if the bus is full. The optional offset argument is added
        to the current number of passengers, e.g.:
        count = 39, offset = 1, capacity = 40 -> bus is full
        """
        return sum(self.pax_dests.itervalues()) + offset == self.route.capacity

    def satisfies(self, dest):
        """
        Checks if the destination is on the bus's route.
        """
        return dest in (stop.stop_id for stop in self.route.stops)

    def dequeue(self, rates):
        """
        Sends the bus on its way.
        """
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

    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.bus_queue = []
        self.pax_dests = PosCounter()
        self.qtime = 0.0
        self.wtime = 0.0

    def __repr__(self):
        return 'Stop({0} | P: {2} | B: {1})'.format(
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
        # <route_id> : <route>
        self.routes = {}
        # <stop_id> : <stop>
        self.stops = {}

    def add_route(self, route_id, stop_ids, bus_count, cap, **kwargs):
        """
        Create a new route and add it to the network. There is no need
        to create the stops since for a valid network there will always
        be roads specifying them.
        """
        stops = []
        for stop_id in stop_ids:
            if stop_id in self.stops:
                stop = self.stops[stop_id]
            else:
                stop = Stop(stop_id)
                self.stops[stop_id] = stop
            stops.append(stop)
        route = Route(route_id, stops, bus_count, cap)
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
