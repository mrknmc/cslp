import unittest
import re

from simulator.parser import InputParser, FLOAT_RX


class TestRouteRegex(unittest.TestCase):

    def setUp(self):
        self.parser = InputParser()

    def test_parse_valid_route(self):
        line = 'route 1 stops 1 2 4 8 buses 4 capacity 50'
        self.parser.parse_line(line)
        # assert self.parser.network contains route 1

    def test_parse_route_without_name(self):
        line = 'route  stops 1 2 3 buses 7 capacity 20'
        self.parser.parse_line(line)
        # assert NoMatches

    def test_parse_route_without_stops(self):
        line = 'route 28 stops buses 9 capacity 10'
        self.parser.parse_line(line)
        # assert NoMatches

    def test_parse_route_without_buses(self):
        line = 'route 22 stops 1 22 49 buses  capacity 100'
        self.parser.parse_line(line)
        # assert NoMatches

    def test_parse_route_without_capacity(self):
        line = 'route 123 stops 0 23 23 2342 65 buses 2 capacity '
        self.parser.parse_line(line)
        # assert NoMatches


class TestRoadRegex(unittest.TestCase):

    def setUp(self):
        self.parser = InputParser()

    def test_valid_road(self):
        line = 'road 12 23 2.1'
        self.parser.parse_line(line)
        # assert it works

    def test_parse_road_without_origin(self):
        line = 'road  23 2.1'
        self.parser.parse_line(line)
        # assert it doesn't work

    def test_parse_road_without_destination(self):
        line = 'road 12  2.1'
        self.parser.parse_line(line)
        # assert it doesn't work

    def test_parse_road_without_rate(self):
        line = 'road 12 23 '
        self.parser.parse_line(line)
        # assert it doesn't work

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
            '0',
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
        )
        for nan in non_numbers:
            match = self.float_rx.match(nan)
            self.assertEqual(match, None, msg=nan)


if __name__ == '__main__':
    unittest.main()
