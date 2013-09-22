

class Event:
    """
    Parent Event class.
    """
    pass


class BusArival(Event):
    """
    Event that represents a bus arriving at a certain bus stop.
    """

    def __init__(self):
        pass

    def __repr__(self):
        return 'Bus {bus_id} arrives at stop {stop_id} at time {time}'.format(
            bus_id=self.bus_id,
            stop_id=self.stop_id
        )


class BusDeparture(Event):
    """
    Event that represents a bus departing a certain bus stop.
    """

    def __init__(self, bus):
        pass

    def __repr__(self):
        return 'Bus {bus_id} leaves stop {stop_id} at time {time}'.format(
            bus_id=self.bus_id,
            stop_id=self,
            time=self.time
        )



class PassengerBoarded(Event):
    """
    Event that represents a passenger boarding a bus at a certain bus stop.
    """

    def __init__(self, bus, passenger):
        # self.bus_id = bus.id
        self.stop_id = bus.current_stop_id()
        self.destination = passenger.destination
        # set TIME

    def __repr__(self):
        return 'Passenger boards bus {bus_id} at stop {stop_id} with \
        destination {destination} at time {time}'.format(
            bus_id=self.bus_id,
            stop_id=self.stop_id,
            self.destination,
            self.time
        )


class PassengerDisembarked(Event):
    """
    Event that represents a passenger disembarking a bus at a certain bus stop.
    """

    def __init__(self, bus):
        # self.bus_id = bus.id
        self.stop_id = bus.current_stop_id()
        # set TIME

    def __repr__(self):
        return 'Passenger disembarks bus {bus_id} at stop {stop_id} at time {time}'.format(
            bus_id=self.bus_id,
            stop_id=self.stop_id,
            time=self.time
        )


class PassengerCreation(Event):
    """
    Event that represents a passenger being created at the origin station with destination.
    """

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        # set TIME

    def __repr__(self):
        return 'A new passenger enters at stop {origin} with destination \
        {destination} at time {time}'.format(
            origin=self.origin,
            destination=self.destination,
            time=self.time
        )
