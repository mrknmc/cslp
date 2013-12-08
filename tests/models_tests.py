import unittest
from unittest import skip

from simulator.models import *


class TestNetwork(unittest.TestCase):

    def setUp(self):
        self.network = Network()


class TestBus(unittest.TestCase):

    def setUp(self):
        self.stops = [Stop(3), Stop(4)]
        self.route = Route(4, self.stops, 2, 20)

    def test_id(self):
        """
        Test that the bus id is set correctly.
        """
        stop = self.stops[0]
        bus = Bus(self.route, 0, stop)
        self.assertEqual(bus.bus_id, '4.0')

    def test_departure_ready(self):
        """
        """
        stop = self.stops[0]
        bus = Bus(self.route, 0, stop)

        bus.pax_dests = {5: 20}
        self.assertTrue(bus.departure_ready)

    def test_disembarks(self):
        """
        Test that there are passengers who want to disembark.
        """
        bus1 = Bus(self.route, 4, self.stops[0])
        bus2 = Bus(self.route, 3, self.stops[1])

        pax_dests = {
            3: 2,
            7: 1,
            9: 1,
            1: 1
        }

        bus1.pax_dests = pax_dests
        bus2.pax_dests = pax_dests

        exit_pax = bus1.disembarks
        self.assertEqual(exit_pax, 2)

        exit_pax = bus2.disembarks
        self.assertEqual(exit_pax, 0)

    def test_full_capacity(self):
        """
        Test that the capacity is full.
        """
        stop = self.stops[0]
        bus = Bus(self.route, 4, stop)

        bus.pax_dests = {5: 19}
        self.assertFalse(bus.full())

        bus.pax_dests[5] += 1
        self.assertTrue(bus.full())


@skip
class TestRoute(unittest.TestCase):

    def setUp(self):
        stops = map(Stop, range(0, 4))
        self.route = Route(1, stops, 8, 10)

    def test_initial_bus_stops(self):
        buses = self.route.buses
        stops = self.route.stops
        self.assertEqual(buses[0].stop.stop_id, 0)
        self.assertEqual(buses[1].stop.stop_id, 1)
        self.assertEqual(buses[2].stop.stop_id, 2)
        self.assertEqual(buses[3].stop.stop_id, 3)
        self.assertEqual(buses[4].stop.stop_id, 0)
        self.assertEqual(buses[5].stop.stop_id, 1)
        self.assertEqual(buses[6].stop.stop_id, 2)
        self.assertEqual(buses[7].stop.stop_id, 3)
        self.assertEqual(len(stops[0].bus_queue), 2)
        self.assertEqual(len(stops[1].bus_queue), 2)
        self.assertEqual(len(stops[2].bus_queue), 2)
        self.assertEqual(len(stops[3].bus_queue), 2)


class TestStop(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
