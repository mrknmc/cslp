import unittest

from random import seed, random
from math import log10

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
        boards = set(self.world.possible_events()['board'])
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
        roads = self.world.network.roads.values()
        buses = list(self.world.network.get_buses())
        for b, r in zip(buses[1:], roads[1:]):
            b.road = list(r)[0]
            b.stop = None
        buses = set(buses[1:])
        arrivals = set(self.world.possible_events()['arrivals'])
        self.assertEqual(buses, arrivals)


class TestTotalRateDelay(unittest.TestCase):
    """
    This test case tests whether the returned total rate and delay are correct.
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

    def test_valid_total_rate(self):
        """
        Tests whether the correct total rate is returned.

        The correct total rate should be:
        0.3 - bus 1.0 on road 1-2
        0.6 - 1 person disembarking 1.1
        0.5 - 1 person boarding 1.1
        0.5 - bus 1.2 ready to depart
        0.4 - passenger creation
        ---
        2.3 - total rate
        """
        buses = self.world.network.routes[1].buses
        stops = self.world.network.routes[1].stops

        # send bus 1.0 on the road
        self.world.dequeue_bus(stops[0])

        # give bus 1.1 some passengers
        buses[1].passengers = [
            Passenger(2, 1),
            Passenger(1, 3),
            Passenger(3, 2)
        ]

        # give the stop some passengers for bus 1.1
        self.world.network.stops[2].passengers = [
            Passenger(2, 3),
            Passenger(7, 5),
            Passenger(2, 5)
        ]

        total_rate = self.world.calculate_total_rate()
        self.assertAlmostEqual(total_rate, 2.3, places=7)  # rounding error

    def test_valid_delay(self):
        """
        Tests whether the correct delay is returned.
        Set the seed so we are guaranteed the same result every time.
        """
        seed(1)
        rand = 0.13436424411240122  # with seed = 1

        total_rate = self.world.calculate_total_rate()
        expected = -(1/total_rate) * log10(rand)
        delay = self.world.sample_delay(total_rate=total_rate)
        self.assertAlmostEqual(delay, expected, places=7)  # rounding error

    def test_choose_event(self):
        """
        Tests whether a valid event was chosen.
        """
        event = self.world.choose_event()
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
