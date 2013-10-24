from collections import defaultdict
from itertools import ifilterfalse, chain, imap
from operator import itemgetter
from random import random, choice
from math import log10

from simulator.util import log, weighted_choice
from simulator.models import Passenger
from simulator.parser import parse_file
from simulator.events import event_dispatch


class World(object):

    def __init__(self, filename=None):
        """
        Initialize the world.
        """
        self.time = 0.0
        if not filename:
            return  # mainly for testing - init the world add params later
        network, params = parse_file(filename)
        self.network = network
        for key, val in params.iteritems():  # this sets all the rates and flags
            setattr(self, key, val)

    def possible_events(self, as_list=False):
        """
        Get all buses that are ready for departure.
        Get all buses that are ready for arrival.

        Get all passengers that are ready to board a bus.
        Get all passengers that are ready to disembark a bus.

        Get a character creation.
        """
        buses = list(self.network.get_buses())
        stops = list(self.network.get_stops())
        events = {
            'disembarks': self.disembarking_passengers(buses=buses),
            'boards': self.boarding_passengers(stops=stops),
            'departs': self.departure_ready_buses(buses=buses),
            'arrivals': self.arrival_ready_buses(buses=buses),
            'new_passengers': [(None, )],
        }
        if list:
            for key, val in events.iteritems():
                events[key] = list(val)
        return events

    def calculate_total_rate(self, events=None):
        """
        Calculates the total rate of all the events.
        """
        if not events:
            events = self.possible_events()

        total_rate = 0
        for key, tups in events.iteritems():
            try:
                total_rate += getattr(self, key) * sum(1 for tup in tups)
            except AttributeError:
                if key != 'arrivals':
                    raise
                total_rate += reduce(lambda t, b: t + b[0].road_rate, tups, 0)

        return total_rate

    def sample_delay(self, total_rate=None):
        """
        Return a sample delay based on total rate.
        """
        if not total_rate:
            total_rate = self.calculate_total_rate()

        mean = 1 / total_rate  # let's hope total_rate won't be 0
        return -mean * log10(random())

    def choose_event(self, events=None, total_rate=None):
        """
        Probabilistically choose one of the events.
        """
        if not events:
            events = self.possible_events()

        if not total_rate:
            total_rate = self.calculate_total_rate(events=events)

        rand = random() * total_rate

        for key, tups in events.iteritems():
            for tup in tups:
                try:
                    rand -= getattr(self, key)
                except AttributeError:
                    rand -= tup[0].road_rate
                if rand < 0:
                    return event_dispatch(self.time, key, *tup)

    def arrival_ready_buses(self, buses=None):
        """
        Return buses that are ready for arrival.
        """
        if not buses:
            buses = self.network.get_buses()

        return ((bus, ) for bus in buses if bus.in_motion)

    def departure_ready_buses(self, buses=None):
        """
        Return buses that are ready for departure.
        """
        if not buses:
            buses = self.network.get_buses()

        return ((bus, ) for bus in buses if bus.ready_for_departure())

    def disembarking_passengers(self, buses=None):
        """
        Returns set of passengers that are at their destination station.
        """
        if not buses:
            buses = self.network.get_buses()

        pax_gens = (bus.disembarking_passengers() for bus in buses if not bus.in_motion)
        return chain(*pax_gens)

    def boarding_passengers(self, stops=None):
        """
        Return passengers that are at their origin station and want to board the bus.
        """
        if not stops:
            stops = self.network.get_stops()

        pax_gens = (stop.boarding_passengers() for stop in stops)
        return chain(*pax_gens)

    def dequeue_bus(self, bus):
        """
        The first bus departs from the queue.
        """
        cur_stop = bus.stop
        cur_stop.bus_queue.remove(bus)
        next_stop = bus.route.get_next_stop(cur_stop.stop_id)  # set next stop
        bus.road_rate = self.network.roads[cur_stop.stop_id, next_stop.stop_id]
        bus.stop = next_stop

    def generate_passenger(self):
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

        dest = choice(dests).stop_id
        orig = orig.stop_id
        return orig, Passenger(orig, dest)

    def generate_passenger(self):
        """
        Generates a passenger on the network.
        """
        orig = choice(self.network.stops)

        dests = []
        for route in self.network.routes.itervalues():
            try:
                idx = route.stops.index(orig)
                dests.extend(routes.stops[:idx])
                dests.extend(routes.stops[idx+1:])
            except ValueError:
                continue

        dest = choice(dests).stop_id
        orig = orig.stop_id
        return orig, Passenger(orig, dest)

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

    def start(self):
        """
        Validate and then start the run loop.
        """
        self.run()

    def run(self):
        """
        Run the simulation until world explodes.
        """
        while self.time <= self.stop_time:
            events = self.possible_events(as_list=True)
            total_rate = self.calculate_total_rate(events=events)
            delay = self.sample_delay(total_rate=total_rate)
            event = self.choose_event(events, total_rate=total_rate)
            event.update_world(self)
            log(event)
            self.time += delay
