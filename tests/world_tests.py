import unittest

from simulator.world import World
from simulator.models import Passenger
from tests.fake_parser import parse_file


class TestPossibleEvents(unittest.TestCase):
    """
    This test case tests whether the correct set of attributes
    was returned.
    """

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
        network, params = parse_file(input_str)
        self.world.network = network
        for key, val in params.iteritems():  # this sets all the rates and flags
            setattr(self.world, key, val)

    def test_possible_disembarks(self):
        """
        Tests whether all possible disembark events were returned.
        """
        pax = (
            [Passenger(1, 2)],
            [Passenger(2, 3), Passenger(1, 2)],
            [Passenger(3, 2), Passenger(1, 3)],
        )
        buses = self.world.network.get_buses()
        for p, b in zip(pax, buses):
            b.passengers = p
        passengers = set([pax[1][1], pax[2][1]])
        disembarks = set(self.world.possible_events()['disembarks'])
        self.assertEqual(passengers, disembarks)
        self.assertEqual(passengers, disembarks)

    def test_possible_boards(self):
        """
        Tests whether all possible board events were returned.
        """
        pax = (
            [Passenger(1, 2), Passenger(1, 3)],
            [],
            [Passenger(3, 2), Passenger(3, 2)],
        )
        stops = self.world.network.get_stops()
        for p, s in zip(pax, stops):
            s.passengers = p
        passengers = set(pax[0] + pax[2])
        boards = set(self.world.possible_events()['boards'])
        self.assertEqual(passengers, boards)

    def test_possible_departs(self):
        """
        Tests whether all possible depart events were returned.
        """
        bus_pax = (
            [Passenger(1, 2)],
            [Passenger(2, 3), Passenger(1, 3)],
            [Passenger(3, 2), Passenger(1, 3)],
        )
        stop_pax = (
            [Passenger(1, 2), Passenger(1, 3)],
            [],
            [Passenger(3, 2), Passenger(3, 2)],
        )
        buses = list(self.world.network.get_buses())
        stops = self.world.network.get_stops()
        for b, p in zip(buses, bus_pax):
            b.passengers = p

        for s, p in zip(stops, stop_pax):
            s.passengers = p

        buses = set([buses[1]])
        departs = set(self.world.possible_events()['departs'])
        self.assertEqual(buses, departs)

    def test_possible_arrivals(self):
        """
        Tests whether all possible arrival events were returned.
        """
        arrival_events = None
        events = self.world.possible_events()
        self.assertTrue(arrival_events.issubset(events))

    def test_possible_creations(self):
        """
        Tests whether all possible passenger creation events were returned.
        """
        creation_events = None
        events = self.world.possible_events()
        self.assertTrue(creation_events.issubset(events))


if __name__ == '__main__':
    unittest.main()
