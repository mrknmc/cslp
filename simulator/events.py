from simulator.models import Passenger


def event_dispatch(time, event_id, *args, **kwargs):
    return {
        'arrivals': BusArrival,
        'departs': BusDeparture,
        'boards': PassengerBoarded,
        'disembarks': PassengerDisembarked,
        'new_passengers': PassengerCreation
    }[event_id](time, *args, **kwargs)


class BusArrival(object):
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
        self.bus.stop.bus_queue.append(self.bus)
        self.bus.road_rate = None


class BusDeparture(object):
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
        world.dequeue_bus(self.bus)


class PassengerBoarded(object):
    """
    Event that represents a passenger boarding a bus at a certain bus stop.
    """

    def __init__(self, time, passenger, bus):
        self.time = time
        self.bus = bus
        self.passenger = passenger

    def __repr__(self):
        return 'Passenger boards bus {bus} at stop {stop} with destination \
{destination} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            destination=self.passenger.dest,
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


class PassengerDisembarked(object):
    """
    Event that represents a passenger disembarking a bus at a certain bus stop.
    """

    def __init__(self, time, passenger, bus):
        self.time = time
        self.bus = bus
        self.passenger = passenger

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


class PassengerCreation(object):
    """
    Event that represents a passenger being created at the origin station with destination.
    """

    def __init__(self, time, *args):
        self.time = time

    def __repr__(self):
        return 'A new passenger enters at stop {origin} with destination {dest} \
at time {time}'.format(
            origin=self.passenger.orig,
            dest=self.passenger.dest,
            time=self.time
        )

    def update_world(self, world):
        """
        Updates the world based on this event.
        Generate a new passenger on some stop that can satisfy his destination.
        """
        orig, passenger = world.generate_passenger()
        self.passenger = passenger
        world.network.stops[orig].passengers.append(passenger)


