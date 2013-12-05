
def log(event_type, **kwargs):
    msgs = {
        'arrivals': 'Bus {bus} arrives at stop {bus.stop} at time {time}',
        'departs': 'Bus {bus} leaves stop {bus.stop} at time {time}',
        'boards': 'Passenger boards bus {bus} at stop {stop} with destination {dest} at time {time}',
        'disembarks': 'Passenger disembarks bus {bus} at stop {stop} at time {time}',
        'new_passengers': 'A new passenger enters at stop {orig} with destination {dest} at time {time}'
    }
    print(msgs[event_type].format(**kwargs))


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
