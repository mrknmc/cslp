import unittest
from simulator.events import *
from simulator.world import World
from fake_parser import parse_file


class TestEventMap(unittest.TestCase):

    def setUp(self):
        input_str = """route 1 stops 1 2 3 buses 3 capacity 10
road 1 2 0.3
road 2 3 0.5
road 3 1 0.8
board 0.5
disembarks 0.6
departs 0.5
new passengers 0.4
stop time 20"""
        self.world = World()
        network, rates, params = parse_file(input_str)
        self.world.event_map = EventMap()
        self.world.network = network
        self.world.rates = rates
        self.world.total_rate = rates['new_passengers']

        # add buses to departs and increment total_rate
        for stop in network.stops.itervalues():
            self.world.event_map.departs.extend(stop.bus_queue)
            self.world.total_rate += len(stop.bus_queue) * rates['departs']

        for key, val in params.iteritems():  # this sets all the rates and flags
            setattr(self.world, key, val)

    def test_event_map_after_boards(self):
        bus = self.world.network.stops[1].bus_queue[0]
        bus.stop.pax_dests = {3: 1}
        kwargs = {'bus': bus, 'dest': 3}

        emap = self.world.event_map

        boards_before = emap.boards[bus][3]
        stop_before = bus.stop.pax_dests[3]
        bus_before = bus.pax_dests[3]
        self.world.update('boards', **kwargs)

        self.assertTrue(emap.boards[bus][3] - boards_before, 1)
        self.assertTrue(stop_before - bus.stop.pax_dests[3], 1)
        self.assertTrue(bus.pax_dests[3] - bus_before, 1)

    def test_event_map_after_disembark(self):
        pass

    def test_event_map_after_depart(self):
        pass

    def test_event_map_after_arrival(self):
        pass

    def test_event_map_after_pax_gen(self):
        pass


if __name__ == '__main__':
    unittest.main()

