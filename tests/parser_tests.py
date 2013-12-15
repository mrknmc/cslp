import unittest
import re

from simulator.parser import *
from simulator.formats import *


class TestRouteRegex(unittest.TestCase):

    def test_parse_valid_route(self):
        params = {
            'route_id': 1,
            'stop_ids': [1, 2, 4, 8],
            'bus_count': 4,
            'cap': 50,
            'ex_caps': None,
            'ex_bus_counts': None
        }
        stop_ids_str = ' '.join(map(str, params['stop_ids']))
        line = 'route {route_id} stops {stop_ids_str} buses {bus_count} capacity {cap}'.format(stop_ids_str=stop_ids_str, **params)
        match = rxmatch(ROUTE_RX, line, fdict=ROUTE_TYPES)
        self.assertEqual(match, params)

    def test_parse_route_without_name(self):
        line = 'route  stops 1 2 3 buses 7 capacity 20'
        self.assertFalse(rxmatch(ROUTE_RX, line, fdict=ROUTE_TYPES))

    def test_parse_route_without_stops(self):
        line = 'route 28 stops buses 9 capacity 10'
        self.assertFalse(rxmatch(ROUTE_RX, line, fdict=ROUTE_TYPES))

    def test_parse_route_without_buses(self):
        line = 'route 22 stops 1 22 49 buses  capacity 100'
        self.assertFalse(rxmatch(ROUTE_RX, line, fdict=ROUTE_TYPES))

    def test_parse_route_without_capacity(self):
        line = 'route 123 stops 0 23 23 2342 65 buses 2 capacity '
        self.assertFalse(rxmatch(ROUTE_RX, line, fdict=ROUTE_TYPES))


class TestRoadRegex(unittest.TestCase):

    def test_valid_road(self):
        params = {
            'orig': 12,
            'dest': 23,
            'rate': 2.1,
            'ex_rates': None
        }
        line = 'road {orig} {dest} {rate}'.format(**params)
        match = rxmatch(ROAD_RX, line, fdict=ROAD_TYPES)
        self.assertEqual(match, params)

    def test_parse_road_without_origin(self):
        line = 'road  23 2.1'
        self.assertFalse(rxmatch(ROAD_RX, line, fdict=ROAD_TYPES))

    def test_parse_road_without_destination(self):
        line = 'road 12  2.1'
        self.assertFalse(rxmatch(ROAD_RX, line, fdict=ROAD_TYPES))

    def test_parse_road_without_rate(self):
        line = 'road 12 23 '
        self.assertFalse(rxmatch(ROAD_RX, line, fdict=ROAD_TYPES))


class TestRatesRegex(unittest.TestCase):

    def test_valid_rates(self):
        tests = (
            ('board', 0.9, 'rate'),
            ('disembarks', 0.4, 'rate'),
            ('departs', 0.3, 'rate'),
            ('new passengers', 0.1, 'rate'),
            ('stop time', 0.7, 'rate'),
        )
        rates_rx = (rx[1] for rx in RATES_RX)
        for rate_rx, test in zip(rates_rx, tests):
            line = "{0} {1}".format(*test)
            self.assertEqual(rxmatch(rate_rx, line, ftype=float), {'rate': test[1], 'ex_rates': None})

    def test_invalid_rates(self):
        tests = (
            'board i',
            'disembarks ',
            'departs ',
            'new passengers',
            'stoptime 2',
        )

        rates_rx = (rx[1] for rx in RATES_RX)
        for rate_rx, test in zip(rates_rx, tests):
            self.assertFalse(rxmatch(rate_rx, test))


class TestFloatRegex(unittest.TestCase):

    def setUp(self):
        self.float_rx = re.compile('^' + FLOAT_RX + '$')

    def test_valid_floats(self):
        numbers = (
            '2.2',
            '2.',
            '.2',
            '.2373219831',
            '2321897.',
            '124124.23231',
            '25',
        )
        for number in numbers:
            match = self.float_rx.match(number)
            self.assertNotEqual(match, None)  # assert it works

    def test_invalid_floats(self):
        non_numbers = (
            '.',
            '',
            '2.2.',
            '2..2',
            '.2.2',
            '.2.',
            '0',
        )
        for nan in non_numbers:
            match = self.float_rx.match(nan)
            self.assertEqual(match, None, msg=nan)


if __name__ == '__main__':
    unittest.main()
