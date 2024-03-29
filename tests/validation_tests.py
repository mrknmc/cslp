import unittest

from simulator.parser import parse_lines
from simulator.models import *
from tests.fake import FakeWorld


class TestNetworkValidation(unittest.TestCase):

    def setUp(self):
        pass

    def test_missing_road_rate_is_error(self):
        """Verifies that when there is no road rate for a road we raise an error."""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 2 3 0.5',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80',
        )
        network, rates, params, experiments = parse_lines(input_str, 'test')
        with self.assertRaises(InputError):
            network.validate(rates, params)

    def test_missing_event_rate_is_error(self):
        """Verifies that when there is no rate for events we raise an error."""
        input_str = '\n'.join((
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.5',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'stop time 80',
        ))
        world = FakeWorld(input_str)
        with self.assertRaises(InputError):
            world.validate()

    def test_missing_stop_time_is_error(self):
        """Verifies that when there is no stop time parameter we raise an error."""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.3',
            'road 2 3 0.5',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_road_rate_for_no_route_is_warn(self):
        """Verifies that when we have a road rate for two stops but no
        route for them we have a warning."""
        input_str = (
            'route 1 stops 1 2 5 buses 3 capacity 10',
            'route 2 stops 1 4 buses 3 capacity 10',
            'road 1 2 0.3',
            'road 1 4 0.3',
            'road 4 1 0.3',
            'road 2 1 0.5',
            'road 2 5 0.8',
            'road 4 5 0.8',
            'road 5 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80'
        )
        network, rates, params, experiments = parse_lines(input_str, 'test')
        with self.assertRaises(InputWarning):
            network.validate(rates, params['ignore_warn'])

    def test_road_rate_for_no_route2_is_warn(self):
        """Verifies that when we have a road rate for two stops but
        at least one of them is not on any route we raise a warning."""
        input_str = (
            'route 1 stops 1 2 buses 3 capacity 10',
            'road 1 2 0.3',
            'road 2 1 0.5',
            'road 4 2 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80'
        )
        network, rates, params, experiments = parse_lines(input_str, 'test')
        with self.assertRaises(InputWarning):
            network.validate(rates, params['ignore_warn'])

    def test_route_with_same_stop_consecutively_is_error(self):
        """Verifies that when we have a route with the same stop twice
        in a row we raise an error."""
        input_str = (
            'route 1 stops 1 1 2 buses 3 capacity 10',
            'road 1 2 0.3',
            'road 2 1 0.5',
            'road 1 1 0.4',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80',
            'ignore warnings'
        )
        network, rates, params, experiments = parse_lines(input_str, 'test')
        with self.assertRaises(InputError):
            network.validate(rates, params)

class TestParserValidation(unittest.TestCase):
    def setUp(self):
        pass

    def test_route_with_one_stop_is_error(self):
        """Verifies that a route with just one stop is an error."""
        input_str = (
            'route 1 stops 1 buses 3 capacity 10',
            'road 2 3 0.5',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80',
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_duplicate_route_is_error(self):
        """Verifies that supplying a route twice raises an error."""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'route 1 stops 3 4 buses 1 capacity 20',
            'road 1 2 0.4',
            'road 2 3 0.5',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80'
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_duplicate_road_is_error(self):
        """Verifies that supplying a road rate twice raises an error."""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.5',
            'road 2 3 0.6',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80'
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_duplicate_stop_time_is_error(self):
        """Verifies that supplying a stop time twice raises an error."""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.6',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 80',
            'stop time 10'
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_duplicate_rate_is_error(self):
        """Verifies that supplying a rate twice raises an error."""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.6',
            'road 3 1 0.8',
            'board 0.5',
            'departs 0.2',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 10'
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_duplicate_optimise_or_ignore_warn_is_error(self):
        """Verifies that supplying the optimise or ignore warning parameters
        twice raises an error"""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.6',
            'road 3 1 0.8',
            'board 0.5',
            'optimise parameters',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 10',
            'optimise parameters'
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.6',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'ignore warnings',
            'departs 0.5',
            'new passengers 5',
            'ignore warnings',
            'stop time 10'
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_missing_optimise_or_ignore_warn_is_not_error(self):
        """Verifies that not supplying the optimise or ignore warning parameters
        is not an error."""
        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.6',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 10'
        )
        try:
            parse_lines(input_str, 'test')
        except InputError:
            self.fail()

        input_str = (
            'route 1 stops 1 2 3 buses 3 capacity 10',
            'road 1 2 0.4',
            'road 2 3 0.6',
            'road 3 1 0.8',
            'board 0.5',
            'disembarks 0.6',
            'departs 0.5',
            'new passengers 5',
            'stop time 10'
        )
        try:
            parse_lines(input_str, 'test')
        except InputError:
            self.fail()

    def test_rate_zero_is_error(self):
        """Verifies that if a rate is 0 we raise an error."""
        input_str = (
            'route 1 stops 1 2 buses 3 capacity 10',
            'road 1 2 0.3',
            'road 2 1 0.2',
            'board 0.4',
            'disembarks 0.5',
            'departs 0',
            'new passengers 3',
            'stop time 80',
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_stop_time_zero_is_error(self):
        """Verifies that stop time cannot be zero."""
        input_str = (
            'route 1 stops 1 2 buses 3 capacity 10',
            'road 1 2 0.3',
            'road 2 1 0.2',
            'board 0.4',
            'disembarks 0.5',
            'departs 0.9',
            'new passengers 3',
            'stop time 0',
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_capacity_zero_is_error(self):
        """Verifies that buses cannot have 0 capacity."""
        input_str = (
            'route 1 stops 1 2 buses 3 capacity 0',
            'road 1 2 0.3',
            'road 2 1 0.2',
            'board 0.4',
            'disembarks 0.5',
            'departs 0.9',
            'new passengers 3',
            'stop time 10',
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_capacity_zero_is_error(self):
        """Verifies that routes cannot have 0 buses."""
        input_str = (
            'route 1 stops 1 2 buses 0 capacity 10',
            'road 1 2 0.3',
            'road 2 1 0.2',
            'board 0.4',
            'disembarks 0.5',
            'departs 0.9',
            'new passengers 3',
            'stop time 10',
        )
        with self.assertRaises(InputError):
            parse_lines(input_str, 'test')

    def test_road_to_itself_is_warn(self):
        """Verifies that a road rate with same stops raises a warning."""
        input_str = (
            'route 1 stops 1 2 buses 3 capacity 10',
            'road 1 2 0.3',
            'road 2 1 0.7',
            'road 1 1 0.2',
            'board 0.4',
            'disembarks 0.5',
            'departs 0.9',
            'new passengers 3',
            'stop time 10',
        )
        with self.assertRaises(InputWarning):
            parse_lines(input_str, 'test')


if __name__ == '__main__':
    unittest.main()

