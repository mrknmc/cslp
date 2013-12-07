from collections import defaultdict, Counter
from functools import partial


def log(event_type, **kwargs):
    msgs = {
        'arrivals': 'Bus {bus} arrives at stop {bus.stop} at time {time}',
        'departs': 'Bus {bus} leaves stop {dest} at time {time}',
        'boards': 'Passenger boards bus {bus} at stop {bus.stop} with destination {dest} at time {time}',
        'disembarks': 'Passenger disembarks bus {bus} at stop {bus.stop} at time {time}',
        'new_passengers': 'A new passenger enters at stop {orig} with destination {dest} at time {time}'
    }
    print(msgs[event_type].format(**kwargs))


def color_log(event_type, **kwargs):
    from termcolor import colored
    msgs = {
        'arrivals': ('Bus {bus} arrives at stop {bus.stop} at time {time}', 'blue'),
        'departs': ('Bus {bus} leaves stop {dest} at time {time}', 'red'),
        'boards': ('Passenger boards bus {bus} at stop {bus.stop} with destination {dest} at time {time}', 'yellow'),
        'disembarks': ('Passenger disembarks bus {bus} at stop {bus.stop} at time {time}', 'cyan'),
        'new_passengers': ('A new passenger enters at stop {orig} with destination {dest} at time {time}', 'magenta')
    }
    print colored('o', msgs[event_type][1]), msgs[event_type][0].format(**kwargs)


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

    def __repr__(self):
        arr = []
        arr.append('')
        arr.append('boards')
        arr.append(str(self.boards))
        arr.append('')
        arr.append('disembarks')
        arr.append(str(self.disembarks))
        arr.append('')
        arr.append('departs')
        arr.append(str(self.departs))
        arr.append('')
        arr.append('arrivals')
        arr.append(str(self.arrivals))
        arr.append('---------------------------------------------------------')
        return '\n'.join(arr)
