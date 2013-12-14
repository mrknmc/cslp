from simulator.world import World
from tests.fake_parser import parse_file
from simulator.events import color_log as log


class FakeWorld(World):

    def __init__(self, input_str):
        self.time = 0.0
        network, rates, params, exps = parse_file(input_str)
        self.network = network
        self.rates = rates
        self.experiments = exps

        # Set all flags
        for key, val in params.iteritems():
            setattr(self, key, val)

    def run(self, stop_at=None):
        """
        Run the simulation until we hit the stop_at event.
        """
        while self.time <= self.stop_time:
            event_type, kwargs = self.choose_event()
            if event_type == stop_at:
                return kwargs
            delay = self.sample_delay()
            self.update(event_type, **kwargs)
            self.time += delay
