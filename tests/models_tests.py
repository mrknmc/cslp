import unittest

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
        bus = Bus(self.route, 0, 20, stop, None)
        self.assertEqual(bus.uid, '4.0')

    def test_ready_for_departure(self):
        """

        """
        stop = self.stops[0]
        bus = Bus(1, None, 20, stop, None)

        bus.in_motion = False
        bus.passengers = [Passenger(4, 5)] * 20
        self.assertTrue(bus.ready_for_departure())

    def test_disembarking_passengers(self):
        """
        Test that there are passengers who want to disembark.
        """
        bus1 = Bus(self.route, 4, 20, self.stops[0], None)
        bus2 = Bus(self.route, 3, 20, self.stops[1], None)

        passengers = [
            Passenger(4, 3),
            Passenger(2, 7),
            Passenger(4, 3),
            Passenger(4, 9),
            Passenger(6, 1),
        ]

        bus1.passengers = passengers
        bus2.passengers = passengers

        exit_pax = list(bus1.disembarking_passengers())

        self.assertTrue(bus1.passengers[0] in exit_pax)
        self.assertTrue(bus1.passengers[2] in exit_pax)
        self.assertEqual(len(exit_pax), 2)

        exit_pax = list(bus2.disembarking_passengers())
        self.assertEqual(exit_pax, [])

    def test_full_capacity(self):
        """
        Test that the capacity is full.
        """
        stop = self.stops[0]
        bus = Bus(self.route, 4, 20, stop, None)

        bus.passengers = [Passenger(4, 5)] * 19
        self.assertFalse(bus.full_capacity())

        bus.board_passenger(Passenger(4, 5))
        self.assertTrue(bus.full_capacity())

        bus.board_passenger(Passenger(4, 5))
        self.assertRaises(Exception, bus.full_capacity)

    def test_no_disembarks(self):
        """
        Test that no one wants to disembark.
        """
        bus1 = Bus(self.route, 4, 20, self.stops[0], None)
        bus2 = Bus(self.route, 4, 20, self.stops[1], None)

        passengers = [
            Passenger(4, 3),
            Passenger(2, 7),
            Passenger(4, 3),
            Passenger(4, 9),
            Passenger(6, 1),
        ]

        bus1.passengers = passengers
        bus2.passengers = passengers

        disembarks = bus1.no_disembarks()
        self.assertEqual(disembarks, False)

        disembarks = bus2.no_disembarks()
        self.assertEqual(disembarks, True)


class TestRoute(unittest.TestCase):

    def setUp(self):
        stops = map(Stop, range(0, 4))
        self.route = Route(1, stops, 8, 10)

    def test_initial_bus_stops(self):
        buses = self.route.buses
        self.assertEqual(buses[0].stop.stop_id, 0)
        self.assertEqual(buses[1].stop.stop_id, 1)
        self.assertEqual(buses[2].stop.stop_id, 2)
        self.assertEqual(buses[3].stop.stop_id, 3)
        self.assertEqual(buses[4].stop.stop_id, 0)
        self.assertEqual(buses[5].stop.stop_id, 1)
        self.assertEqual(buses[6].stop.stop_id, 2)
        self.assertEqual(buses[7].stop.stop_id, 3)


class TestStop(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
