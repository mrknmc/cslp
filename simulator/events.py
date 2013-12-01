
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

    def __init__(self, time, dest, bus):
        self.time = time
        self.bus = bus
        self.dest = dest

    def __repr__(self):
        return 'Passenger boards bus {bus} at stop {stop} with destination \
{dest} at time {time}'.format(
            bus=self.bus,
            stop=self.bus.stop,
            dest=self.dest,
            time=self.time
        )

    def update_world(self, world):
        """
        Updates the world based on this event.
        Remove the passenger from the bus stop and board him on the bus.
        """
        stop = self.bus.stop
        stop.pax_dests[self.dest] -= 1
        self.bus.pax_dests[self.dest] += 1


class PassengerDisembarked(object):
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
        self.bus.pax_dests[self.bus.stop] -= 1


class PassengerCreation(object):
    """
    Event that represents a passenger being created at the origin station with destination.
    """

    def __init__(self, time, *args):
        self.time = time

    def __repr__(self):
        return 'A new passenger enters at stop {origin} with destination {dest} \
at time {time}'.format(
            origin=self.orig,
            dest=self.dest,
            time=self.time
        )

    def update_world(self, world):
        """
        Updates the world based on this event.
        Generate a new passenger on some stop that can satisfy his destination.
        """
        self.orig, self.dest = world.generate_passenger()
        world.network.stops[self.orig].pax_dests[self.dest] += 1


