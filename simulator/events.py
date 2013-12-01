
def event_dispatch(time, event_id, *args, **kwargs):
    return {
        'arrivals': BusArrival,
        'departs': BusDeparture,
        'boards': PassengerBoarded,
        'disembarks': PassengerDisembarked,
        'new_passengers': PassengerCreation
    }[event_id](time, *args, **kwargs)


class EventMap(object):
    """
    Dictionary-like data structure to hold all possible events.
    """

    def __init__(self, world):
        self.events = {
            'boards': 0,
            'disembarks': 0,
            'departs': 0,
            'arrivals': 0,
            'new_passengers': 1,
        }
        self.world = world
        self.last_event = None

    # def total_rate(self):
        # pass

    def sample_delay(self):
        """
        Return a sample delay based on the total rate.
        """
        mean = 1 / self.total_rate
        return -mean * log10(random())

    def update(self, event):
        """
        Update the event map based on the last event picked.
        Update the total rate based on the last event picked.
        """
        if event.type == 'boards':
            bus = event.bus
            stop = bus.stop
            dest = event.dest
            for bus in stop.bus_queue:
                self.total_rate -= self.world.boards  # Decrement the total rate by number of buses
                self.map['boards'][bus.bus_id][dest] -= 1  # Remove dest from boards of other buses
            if bus.full_capacity():
                self.total_rate += self.world.
                self.map['departs'].append(bus)  # Update 'departs'
                del(self.map['boards'][bus.bus_id])  # Remove 'boarders' of this bus
        elif event.type == 'disembarks':
            bus = event.bus
            stop_id = bus.stop.stop_id
            self.map['disembarks'][bus.bus_id][stop_id] -= 1
            if bus.full_capacity():
                self.map['boards'][bus.bus_id] = dict(bus.boarders())  # Add boards if bus was full
        elif event.type == 'departs':
            bus = event.bus
            # Update 'arrivals'
            self.map['arrivals'].append(bus)
        elif event.type == 'arrivals':
            bus = event.bus
            # Update 'boarders'
            self.map['boards'][bus.bus_id] = dict(bus.boarders())
            # Update 'disembarkers'
            self.map['disembarks'][bus.bus_id] = dict(bus.disembarkers())
        else:
            # Passenger creation
            orig = event.orig
            dest = event.dest
            buses = self.world.network.stops[orig].bus_queue
            for bus in buses:
                if bus.can_satisfy(dest):
                    self.map['boards'][bus.bus_id][dest] += 1
            # Update 'boarders'
        # Recalculate the total rate
        pass

    def choose_event(self):
        """
        Chooses an event based on the last event.
        """
        rand = random() * total_rate

        for key, tups in events.iteritems():
            for tup in tups:
                try:
                    rand -= getattr(self.world, key)
                except AttributeError:
                    rand -= tup[0].road_rate
                if rand < 0:
                    return event_dispatch(self.time, key, *tup)


class BusArrival(object):
    """
    Event that represents a bus arriving at a certain bus stop.
    """

    type = 'arrivals'

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

    type = 'departs'

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

    type = 'boards'

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

    type = 'disembarks'

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

    type = 'new_passengers'

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


