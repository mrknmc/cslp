from collections import defaultdict, Counter
from lib.termcolor import colored

from simulator.formats import EVENTS, EVENT_COLOURS


def log_event(event_type, **kwargs):
    """Logs an event to the output."""
    print(EVENTS[event_type].format(**kwargs))


def color_log(event_type, **kwargs):
    """Logs a colored event to the output."""
    print('{} {}'.format(
        colored('o', EVENT_COLOURS[event_type]),
        EVENTS[event_type].format(**kwargs)
    ))


class EventMap(object):
    """
    Dictionary-like data structure to hold all possible events.
    """

    def __init__(self):
        self.board = defaultdict(PosCounter)
        self.disembarks = []
        self.departs = []
        self.arrivals = []

    def gen_board(self):
        """Generates triples of bus, destination and count of possible
        board events."""
        for bus, dct in self.board.iteritems():
            for dest, count in dct.iteritems():
                yield bus, dest, count

    def __repr__(self):
        return '\n'.join([
            '',
            'board',
            str(self.board),
            '',
            'disembarks',
            str(self.disembarks),
            '',
            'departs',
            str(self.departs),
            '',
            'arrivals',
            str(self.arrivals),
            '---------------------------------------------------------',
        ])


class PosCounter(Counter):
    """
    Convenience subclass of Counter that removes a key-value pair
    when value is less than or equal to 0.
    """

    def __setitem__(self, key, val):
        if val <= 0:
            self.__delitem__(key)
        else:
            super(Counter, self).__setitem__(key, val)
