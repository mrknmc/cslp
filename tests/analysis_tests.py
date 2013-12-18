import unittest
from random import choice

from tests.fake import FakeWorld
from simulator.models import *


class TestAnalysis(unittest.TestCase):

    def setUp(self):
        input_str = """
route 1 stops 1 2 3 buses 3 capacity {}
road 1 2 0.3
road 2 3 0.5
road 3 1 0.8
board 0.5
disembarks 0.6
departs 0.5
new passengers 5
stop time 80
""".format(choice([1, 3, 20]))
        self.world = FakeWorld(input_str)
        self.world.initialise()

    def test_missed_pax_incremented_after_departs(self):
        """This verifies that the Number of Missed Passengers is
        incremented after a departs event if the bus is full."""
        kwargs = self.world.run(stop_at='departs')

        bus = kwargs['bus']
        stop_id = bus.stop.stop_id
        route_id = bus.route.route_id
        stop_pax_count = sum(bus.stop.pax_dests.itervalues())

        missed_stop = self.world.analysis['missed_pax']['stop'][stop_id]
        missed_route = self.world.analysis['missed_pax']['route'][route_id]

        # Update the world to confirm
        self.world.update('departs', **kwargs)
        now_stop = self.world.analysis['missed_pax']['stop'][stop_id]
        now_route = self.world.analysis['missed_pax']['route'][route_id]

        if bus.full() and stop_pax_count:
            self.assertTrue(missed_stop + stop_pax_count == now_stop, msg='{} < {}'.format(missed_stop, now_stop))
            self.assertTrue(missed_route + stop_pax_count == now_route, msg='{} < {}'.format(missed_route, now_route))
        else:
            self.assertTrue(missed_stop == now_stop, msg='{} < {}'.format(missed_stop, now_stop))
            self.assertTrue(missed_route == now_route, msg='{} < {}'.format(missed_stop, now_stop))

    def test_missed_pax_not_incremented_after_other_events(self):
        """This verifies that the Number of Missed Passengers is not
        incremented after any other event."""
        event_type = choice(['arrivals', 'board', 'new_passengers', 'disembarks'])
        kwargs = self.world.run(stop_at=event_type)

        if self.world.time >= self.world.stop_time:
            return  # Event did not happen

        missed_stop = self.world.analysis['missed_pax']['stop']
        missed_route = self.world.analysis['missed_pax']['route']

        # Update the world to confirm
        self.world.update(event_type, **kwargs)
        now_stop = self.world.analysis['missed_pax']['stop']
        now_route = self.world.analysis['missed_pax']['route']

        self.assertTrue(missed_stop == now_stop, msg='{} < {}'.format(missed_stop, now_stop))
        self.assertTrue(missed_route == now_route, msg='{} < {}'.format(missed_stop, now_stop))

    def test_avg_pax_incremented_after_departs(self):
        """This verifies that the Average Passengers Per Bus Per Road is
        incremented after a departs event."""
        kwargs = self.world.run(stop_at='departs')

        bus = kwargs['bus']
        bus_pax = sum(bus.pax_dests.itervalues())
        avg_pax_count, avg_pax_sum = self.world.analysis['avg_pax'][bus.bus_id]
        self.world.update('departs', **kwargs)

        self.assertTrue((avg_pax_count + 1, avg_pax_sum + bus_pax) == self.world.analysis['avg_pax'][bus.bus_id])

    def test_avg_pax_not_incremented_after_other_events(self):
        """This verifies that the Average Passengers Per Bus Per Road is not
        incremented after any other event."""
        event_type = choice(['arrivals', 'board', 'new_passengers', 'disembarks'])
        kwargs = self.world.run(stop_at=event_type)

        if self.world.time >= self.world.stop_time:
            return  # Event did not happen

        avg_pax = self.world.analysis['avg_pax']
        self.world.update(event_type, **kwargs)

        self.assertTrue(avg_pax == self.world.analysis['avg_pax'])

    def test_avg_qtime_incremented_after_departs_or_arrivals(self):
        """This verifies that the Average Bus Queuing Time is incremented
        after a departs or arrivals event."""
        event_type = choice(['arrivals', 'departs'])
        kwargs = self.world.run(stop_at=event_type)
        stop = kwargs['bus'].stop

        time_diff = self.world.time - stop.qtime
        wait = stop.queue_length * time_diff

        qtime = self.world.analysis['avg_qtime'][stop.stop_id]
        self.world.update(event_type, **kwargs)

        self.assertTrue(qtime + wait == self.world.analysis['avg_qtime'][stop.stop_id])

    def test_avg_qtime_not_incremented_after_other_events(self):
        """This verifies that the Average Bus Queuing Time is not incremented
        after any other event."""
        event_type = choice(['disembarks', 'board', 'new_passengers'])
        kwargs = self.world.run(stop_at=event_type)

        if self.world.time >= self.world.stop_time:
            return  # Event did not happen

        avg_qtime = self.world.analysis['avg_qtime']
        self.world.update(event_type, **kwargs)

        self.assertTrue(avg_qtime == self.world.analysis['avg_qtime'])

    # def test_avg_wtime_incremented_after_new_passengers_or_board(self):
    #     """This verifies that the Average Waiting Passengers is incremented
    #     after a new_passengers or board event."""
    #     event_type = choice(['board', 'new_passengers'])
    #     kwargs = self.world.run(stop_at=event_type)

    #     bus = kwargs['bus']
    #     stop_id = bus.stop.stop_id
    #     # route_id = bus.route.route_id

    #     stop_wtime = self.world.analysis['avg_wtime']['stop'][stop_id]
    #     # route_wtime = self.world.analysis['avg_wtime']['route'][route_id]

    #     self.world.update(event_type, **kwargs)

    #     self.assertTrue(stop_wtime < self.world.analysis['avg_wtime']['stop'][stop_id])
    #     # self.assertTrue(route_wtime < self.world.analysis['avg_wtime']['route'][route_id])

if __name__ == '__main__':
    suite = unittest.TestSuite()

    for i in xrange(100):
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAnalysis))
    unittest.TextTestRunner().run(suite)
