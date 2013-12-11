from collections import defaultdict, Counter

from lib.termcolor import colored

from formats import EVENTS, EVENT_COLOURS


def log_event(event_type, **kwargs):
    print(EVENTS[event_type].format(**kwargs))


def color_log(event_type, **kwargs):
    print(colored('o', EVENT_COLOURS[event_type]), EVENTS[event_type].format(**kwargs))


class EventMap(object):
    """
    Dictionary-like data structure to hold all possible events.
    """

    def __init__(self):
        self.boards = defaultdict(lambda: PosCounter())
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


class PosCounter(Counter):

    def __setitem__(self, key, val):
        if val <= 0:
            self.__delitem__(key)
        else:
            super(Counter, self).__setitem__(key, val)
