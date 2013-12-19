import unittest

# from simulator.world import InputError, InputWarning
from tests.fake import FakeWorld
from simulator.models import *


class TestDepartsUpdate(unittest.TestCase):

    def setUp(self):
        input_str = """
route 1 stops 1 2 3 4 5 6 buses 3 capacity 10
route 2 stops 2 4 8 9 3 6 buses 2 capacity 8
road 1 2 0.3
road 2 3 0.5
road 3 4 0.8
road 4 5 0.2
road 5 6 0.5
road 6 1 0.2
road 2 4 0.1
road 4 8 0.6
road 8 9 0.7
road 9 3 0.2
road 3 6 0.4
road 6 2 0.3
board 0.5
disembarks 0.6
departs 0.5
new passengers 4
stop time 1000
"""

        self.world = FakeWorld(input_str)
        self.world.initialise()

    def test_no_boards_before_departs(self):
        """Verifies that there are no potential boarders
        on the bus stop before the bus departs from the bus stop."""
        kwargs = self.world.run(stop_at='departs', after=20)
        bus = kwargs['bus']

        if not bus.full():
            list(bus.boards) == []

    def test_no_disembarks_before_departs(self):
        """Verifies that there are no potential disembarkers
        on the bus before the bus departs form the bus stop."""
        kwargs = self.world.run(stop_at='departs', after=20)
        bus = kwargs['bus']

        self.assertEqual(bus.disembarks, 0)

    def test_bus_on_head_full_or_no_boarders_before_departs(self):
        """Verifies that the bus was either on the head of the bus queue,
        full or there are no boarders before it departs from the stop."""
        kwargs = self.world.run(stop_at='departs', after=60)
        bus = kwargs['bus']

        self.assertTrue(bus.departure_ready)


class TestArrivalsUpdate(unittest.TestCase):

    def setUp(self):
        input_str = """
route 1 stops 1 2 3 4 5 6 buses 3 capacity 10
route 2 stops 2 4 8 9 3 6 buses 2 capacity 8
road 1 2 0.3
road 2 3 0.5
road 3 4 0.8
road 4 5 0.2
road 5 6 0.5
road 6 1 0.2
road 2 4 0.1
road 4 8 0.6
road 8 9 0.7
road 9 3 0.2
road 3 6 0.4
road 6 2 0.3
board 0.5
disembarks 0.6
departs 0.5
new passengers 4
stop time 1000
"""
        self.world = FakeWorld(input_str)
        self.world.initialise()

    def test_bus_in_motion_before_arrival(self):
        """Verifies that the bus is in motion before its arrival."""
        kwargs = self.world.run(stop_at='arrivals', after=20)
        bus = kwargs['bus']

        self.assertTrue(bus.in_motion)


if __name__ == '__main__':
    suite = unittest.TestSuite()

    for i in xrange(100):
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDepartsUpdate))
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestArrivalsUpdate))
    unittest.TextTestRunner().run(suite)
