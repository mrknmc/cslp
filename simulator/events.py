

def event_dispatch(time, event_id, *args, **kwargs):
    return {
        'arrivals': BusArrival,
        'departs': BusDeparture,
        'board': PassengerBoarded,
        'disembarks': PassengerDisembarked,
        'new_passengers': PassengerCreation
    }[event_id](time, *args, **kwargs)


class BusArrival:
    """
    Event that represents a bus arriving at a certain bus stop.
    """

    def __init__(self, time, bus):
        self.time = time
        self.bus = bus

    def __repr__(self):
        return 'Bus {bus} arrives at stop {stop} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            time=self.time
        )

    def update_world(self, world):
        """
        Updates the world based on this event.
        """
        world.enqueue_bus(self.bus)


class BusDeparture:
    """
    Event that represents a bus departing a certain bus stop.
    """

    def __init__(self, time, bus):
        self.time = time
        self.bus = bus

    def __repr__(self):
        return 'Bus {bus} leaves stop {stop} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            time=self.time
        )

    def update_world(self, world):
        """
        Updates the world based on this event.
        Dequeue bus from the bus stop
        """
        world.dequeue_bus(bus)


class PassengerBoarded:
    """
    Event that represents a passenger boarding a bus at a certain bus stop.
    """

    def __init__(self, time, bus, passenger):
        self.time = time
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

    def update_world(self, world):
        """
        Updates the world based on this event.
        Remove the passenger from the bus stop and board him on the bus.
        """
        stop = self.bus.stop
        stop.passengers.remove(self.passenger)
        self.bus.passengers.append(self.passenger)


class PassengerDisembarked:
    """
    Event that represents a passenger disembarking a bus at a certain bus stop.
    """

    def __init__(self, time, bus):
        self.time = time
        self.bus = bus

    def __repr__(self):
        return 'Passenger disembarks bus {bus} at stop {stop} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            time=self.time
        )

    def update_world(self, world):
        """
        Updates the world based on this event.
        Remove the passenger from the bus.
        """
        self.bus.passengers.remove(self.passenger)


class PassengerCreation:
    """
    Event that represents a passenger being created at the origin station with destination.
    """

    def __init__(self, time, origin, destination):
        self.time = time
        self.origin = origin
        self.destination = destination

    def __repr__(self):
        return 'A new passenger enters at stop {origin} with destination {dest} \
        at time {time}'.format(
            origin=self.origin,
            dest=self.destination,
            time=self.time
        )

    def update_world(self, world):
        """
        Updates the world based on this event.
        Generate a new passenger on some stop that can satisfy his destination.
        """
        pass

