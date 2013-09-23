import unittest

from simulator.models import Network, Route, Bus, Passenger


class TestNetwork(unittest.TestCase):

    def setUp(self):
        self.network = Network()


class TestBus(unittest.TestCase):

    def setUp(self):
        pass

    def test_id(self):
        """
        Test that the bus id is set correctly.
        """
        bus = Bus(12, 4, 20, 4)
        self.assertEqual(bus.uid, '12.4')

    def test_ready_for_departure(self):
        """

        """
        bus = Bus(1, 0, 20, 2)

        bus.in_motion = False
        bus.passengers = [Passenger(4, 5)] * 20
        self.assertTrue(bus.ready_for_departure())
        # TODO: finish this

    def test_disembarking_passengers(self):
        """
        Test that there are passengers who want to disembark.
        """
        bus1 = Bus(12, 4, 20, 5)
        bus2 = Bus(12, 4, 20, 2)

        passengers = [
            Passenger(4, 5),
            Passenger(2, 7),
            Passenger(4, 5),
            Passenger(4, 9),
            Passenger(6, 1),
        ]

        bus1.passengers = passengers
        bus2.passengers = passengers

        exit_pax = bus1.disembarking_passengers()

        self.assertTrue(bus1.passengers[0] in exit_pax)
        self.assertTrue(bus1.passengers[2] in exit_pax)
        self.assertEqual(len(exit_pax), 2)

        exit_pax = bus2.disembarking_passengers()
        self.assertEqual(exit_pax, [])

    def test_full_capacity(self):
        """
        Test that the capacity is full.
        """
        bus = Bus(12, 4, 20, 5)

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
        bus1 = Bus(12, 4, 20, 5)
        bus2 = Bus(12, 4, 20, 2)

        passengers = [
            Passenger(4, 5),
            Passenger(2, 7),
            Passenger(4, 5),
            Passenger(4, 9),
            Passenger(6, 1),
        ]

        bus1.passengers = passengers
        bus2.passengers = passengers

        disembarks = bus1.no_disembarks()
        self.assertEqual(disembarks, False)

        disembarks = bus2.no_disembarks()
        self.assertEqual(disembarks, True)


class TestStop(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
