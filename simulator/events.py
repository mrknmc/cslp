
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

    def __init__(self, network=None):
        self.boards = {}
        self.disembarks = {}
        self.departs = []
        self.arrivals = []
        # Initialise the network
        if network:
            for stop in network.stops.itervalues():
                self.departs.extend(stop.bus_queue)

    def gen_boards(self):
        for bus, dct in self.boards.iteritems():
            for dest, count in dct.iteritems():
                yield bus, dest, count

    def gen_disembarks(self):
        for bus, dct in self.disembarks.iteritems():
            for dest, count in dct.iteritems():
                yield bus, dest, count
