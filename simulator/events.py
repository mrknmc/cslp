from collections import defaultdict, Counter
from functools import partial
from termcolor import colored


def log(event_type, **kwargs):
    msgs = {
        'arrivals': 'Bus {bus} arrives at stop {bus.stop} at time {time}',
        'departs': 'Bus {bus} leaves stop {dest} at time {time}',
        'boards': 'Passenger boards bus {bus} at stop {bus.stop} with destination {dest} at time {time}',
        'disembarks': 'Passenger disembarks bus {bus} at stop {bus.stop} at time {time}',
        'new_passengers': 'A new passenger enters at stop {orig} with destination {dest} at time {time}'
    }
    print(msgs[event_type].format(**kwargs))


class EventMap(object):
    """
    Dictionary-like data structure to hold all possible events.
    """

    def __init__(self):
        self.boards = defaultdict(lambda: Counter())
        self.disembarks = []
        self.departs = []
        self.arrivals = []

    def gen_boards(self):
        for bus, dct in self.boards.iteritems():
            for dest, count in dct.iteritems():
                yield bus, dest, count

