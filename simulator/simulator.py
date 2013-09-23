

class Simulator:

    def __init__(self, max_time):
        self.max_time = max_time
        self.time = 0.0
        # self.network = PARSE A FILE


    def possible_events(self):
        """
        Get all buses that are ready for departure.
        Get all buses that are ready for arrival.

        Get all passengers that are ready to board a bus.
        Get all passengers that are ready to disembark a bus.

        Get a characted creation.
        """
        for route, route_dict in self.network.routes.iteritems():
            dep_buses = self.ready_buses(route_dict["buses"])
            # handle route_dict["stops"]

    def ready_buses(self, buses):
        """
        Return buses that are ready for departure.
        """
        # return filter(lambda b: b.read_for_departure(), buses)
        return [bus for bus in buses if bus.read_for_departure()]

    def ready_stops(self):
        pass

    def run(self):
        while self.time <= self.max_time:
            pass  # From the current state calculate the set of events which may occur total rate ← the sum of the rates of those events
            pass  # delay ← choose a delay based on the total rate
            pass  # event ← choose probabilistically from those events
            pass  # modify the state of the system based on the chosen event
            pass  # time ← time + delay


if __name__ == '__main__':
    main()
