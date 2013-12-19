from simulator.world import World
from simulator.parser import *


class FakeWorld(World):

    def __init__(self, input_str):
        self.time = 0.0
        self.wtime = 0.0
        input_lst = input_str.splitlines(True)
        network, rates, params, exps = parse_lines(input_lst, 'test')
        self.network = network
        self.rates = rates
        self.experiments = exps

        # Set all flags
        for key, val in params.iteritems():
            setattr(self, key, val)

    def run(self, stop_at=None, after=0, conds=None):
        """
        Run the simulation until we hit the stop_at or conds event.
        """
        while self.time <= self.stop_time:
            event_type, kwargs = self.choose_event()
            if conds and event_type == stop_at:
                if self.satisfies_conds(conds, **kwargs):
                    return kwargs
            if event_type == stop_at and self.time > after:
                return kwargs
            delay = self.sample_delay()
            self.update(event_type, **kwargs)
            self.time += delay

    def satisfies_conds(self, conds, **kwargs):
        """Returns true if the simulation satisfies conditions"""
        for key, funcs in conds.iteritems():
            all((func(kwargs[key]) for func in funcs))
