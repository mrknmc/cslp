

class Event:
    """
    Parent Event class.
    """
    def __init__(self):
        # SOMEHOW GET THE TIME
        pass


class BusArrival(Event):
    """
    Event that represents a bus arriving at a certain bus stop.
    """

    def __init__(self, bus):
        self.bus = bus

    def __repr__(self):
        return 'Bus {bus} arrives at stop {stop} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            time=self.time
        )


class BusDeparture(Event):
    """
    Event that represents a bus departing a certain bus stop.
    """

    def __init__(self, bus):
        self.bus = bus

    def __repr__(self):
        return 'Bus {bus} leaves stop {stop} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            time=self.time
        )



class PassengerBoarded(Event):
    """
    Event that represents a passenger boarding a bus at a certain bus stop.
    """

    def __init__(self, bus, passenger):
        self.bus = bus
        self.destination = passenger.destination

    def __repr__(self):
        return 'Passenger boards bus {bus} at stop {stop} with destination \
        {destination} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            destination=self.destination,
            time=self.time
        )


class PassengerDisembarked(Event):
    """
    Event that represents a passenger disembarking a bus at a certain bus stop.
    """

    def __init__(self, bus):
        self.bus = bus

    def __repr__(self):
        return 'Passenger disembarks bus {bus} at stop {stop} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            time=self.time
        )


class PassengerCreation(Event):
    """
    Event that represents a passenger being created at the origin station with destination.
    """

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination

    def __repr__(self):
        return 'A new passenger enters at stop {origin} with destination {dest} \
        at time {time}'.format(
            origin=self.origin,
            dest=self.destination,
            time=self.time
        )
