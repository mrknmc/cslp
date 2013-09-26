from simulator.parser import InputParser

class Simulator:

    def __init__(self, filename):
        """
        Initialize the simulator with some default values.
        """
        # self.create_network(filename)  # TODO: maybe a bad idea?
        # self.network = PARSE A FILE
        self.time = 0.0
        self.board_rate = None
        self.disembark_rate = None
        self.depart_rate = None
        self.new_passengers_rate = None
        self.stop_time = None

    def create_network(self, filename):
        """
        Create a network from the passed in input file.
        """
        parser = InputParser()
        self.network = parser.parse_file(filename)

    def possible_events(self):
        """
        Get all buses that are ready for departure.
        Get all buses that are ready for arrival.

        Get all passengers that are ready to board a bus.
        Get all passengers that are ready to disembark a bus.

        Get a characted creation.
        """
        # TODO: Maybe move this function into Network object
        for route, route_dict in self.network.routes.iteritems():
            buses = route_dict["buses"]
            dep_buses = self.departure_ready_buses(buses)  # all the buses that want to depart from their bus stop
            arr_buses = self.arrival_ready_buses(buses)  # all the buses that want to arrive to their next bus stop
            board_pax = self.boarding_passengers(stops)  # all the passengers that want to board a bus
            exit_pax = self.disembarking_passengers(buses)  # all the passengers that want to disembark their bus
            # TODO: don't forget a passenger creation here!

            # handle route_dict["stops"]

    def departure_ready_buses(self, buses):
        """
        Return buses that are ready for departure.
        """
        # return filter(lambda b: b.ready_for_departure(), buses)
        return [bus for bus in buses if bus.ready_for_departure()]

    def disembarking_passengers(self, buses):
        """
        Return passengers that are at their destination station.
        """
        passengers = []
        for bus in buses:
            if not bus.in_motion:
                passengers += bus.disembarking_passengers()

        return passengers

    def boarding_passengers(self, stops):
        """
        Return passengers that are at their origin station and want to board the bus.
        """
        board_passengers = []
        for stop in stops:
            # TODO: work-out how to satisfy a passenger's destination
            passengers = [pax for pax in passengers if stop.can_board(pax)]
            board_passengers.append(passengers)

        return board_passengers

    def validate(self):
        """
        If any of the needed rates was not set the simulation is not valid.

        Next, validate the network.
        """
        if any([
            self.board_rate is None,
            self.disembark_rate is None,
            self.departs_rate is None,
            self.new_passengers_rate is None,
            max_time is None
        ]):
            raise Exception("The simulation is not valid.")
        self.network.validate()

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


if __name__ == '__main__':
    main()
