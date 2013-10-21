from collections import defaultdict
from itertools import ifilterfalse, chain, imap

from simulator.models import Bus
from simulator.parser import parse_file


class World:

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
            setattr(self.world, key, val)

    def possible_events(self):
        """
        Get all buses that are ready for departure.
        Get all buses that are ready for arrival.

        Get all passengers that are ready to board a bus.
        Get all passengers that are ready to disembark a bus.

        Get a characted creation.
        """
        # TODO: Maybe move this function into Network object
        buses = list(self.network.get_buses())
        stops = list(self.network.get_stops())
        events = {
            'disembarks': self.disembarking_passengers(buses=buses),
            'boards': self.boarding_passengers(stops=stops),
            'departs': self.departure_ready_buses(buses=buses)  # all the buses that want to depart from their bus stop
        }
        # events['arr_buses'].update(self.arrival_ready_buses(buses))  # all the buses that want to arrive to their next bus stop
        # TODO: don't forget a passenger creation here!

            # handle route_dict["stops"]
        return events

    def departure_ready_buses(self, buses):
        """
        Return buses that are ready for departure.
        """
        return (bus for bus in buses if bus.ready_for_departure())

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

    def validate(self):
        """
        If any of the needed rates was not set the simulation is not valid.

        Next, validate the network.
        """
        if any([
            self.board_rate is None,
            self.disembark_rate is None,
            self.depart_rate is None,
            self.new_passengers_rate is None,
            self.stop_time is None
        ]):
            raise Exception("The simulation is not valid.")
        self.network.validate()

    def start(self):
        """
        Validate and then start the run loop.
        """
        self.validate()
        self.run()

    def run(self):
        """
        Run the simulation until world explodes.
        """
        while self.time <= self.max_time:
            pass  # From the current state calculate the set of events which may occur total rate <- the sum of the rates of those events
            pass  # delay <- choose a delay based on the total rate
            pass  # event <- choose probabilistically from those events
            pass  # modify the state of the system based on the chosen event
            pass  # time <- time + delay
