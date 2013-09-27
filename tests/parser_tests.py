import unittest
import re

from simulator.parser import InputParser, FLOAT_RX


class TestRouteRegex(unittest.TestCase):

    def setUp(self):
        self.parser = InputParser()

    def test_parse_valid_route(self):
        params = {
            'id': 1,
            'stops': ' '.join(['1','2','4','8']),
            'count': 4,
            'cap': 50
        }
        line = 'route {id} stops {stops} buses {count} capacity {cap}'.format(**params)
        self.parser.parse_line(line)
        route = self.parser.network.routes[params['id']]
        self.assertEqual(route.route_id, params['id'])
        self.assertEqual(route.stop_ids, map(int, params['stops'].split(' ')))
        self.assertEqual(len(route.buses), params['count'])
        self.assertEqual(route.buses[0].capacity, params['cap'])

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
        params = {
            'orig': 12,
            'dest': 23,
            'rate': 2.1
        }
        line = 'road {orig} {dest} {rate}'.format(**params)
        self.parser.parse_line(line)
        roads = self.parser.network.roads[params['orig']]
        self.assertEqual(len(roads), 1)
        road = roads.pop()
        self.assertEqual(road.origin, params['orig'])
        self.assertEqual(road.destination, params['dest'])
        self.assertEqual(road.rate, params['rate'])

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


class TestRatesRegex(unittest.TestCase):

    def setUp(self):
        self.parser = InputParser()

    def test_valid_boards_rate(self):
        line = 'board 0.9'
        self.parser.parse_line(line)
        self.assertEqual(self.parser.sim.boards_rate, 0.9)

    def test_invalid_boards_rate(self):
        line = 'board i'
        self.parser.parse_line(line)
        # assert NoMatches

    def test_valid_disembarks_rate(self):
        line = 'disembarks 2.3'
        self.parser.parse_line(line)
        self.assertEqual(self.parser.sim.disembarks_rate, 2.3)

    def test_invalid_disembarks_rate(self):
        line = 'disembarks '
        self.parser.parse_line(line)
        # assert NoMatches

    def test_valid_departs_rate(self):
        line = 'departs 0.3'
        self.parser.parse_line(line)
        self.assertEqual(self.parser.sim.departs_rate, 0.3)

    def test_invalid_departs_rate(self):
        line = 'departs  '
        self.parser.parse_line(line)
        # assert NoMatches

    def test_valid_new_passengers_rate(self):
        line = 'new passengers 7'
        self.parser.parse_line(line)
        self.assertEqual(self.parser.sim.new_passengers_rate, 7)

    def test_invalid_new_passengers_rate(self):
        line = 'new passengers'
        self.parser.parse_line(line)
        # assert NoMatches

    def test_valid_stop_time(self):
        line = 'stop time 2'
        self.parser.parse_line(line)
        self.assertEqual(self.parser.sim.stop_time, 2)

    def test_invalid_stop_time(self):
        line = 'stoptime 2'
        self.parser.parse_line(line)
        # assert NoMatches


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
