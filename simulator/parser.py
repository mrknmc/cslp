import re

from models import Network

INT_RX = r'\d+'
FLOAT_RX = r'(\d+(\.\d*)?|\.\d+)'

ROUTE_RX = r'^route (?P<route_id>{0}) stops (?P<stop_ids>{0}( {0})*) buses (?P<bus_count>{0}) capacity (?P<bus_capacity>{0})$'.format(INT_RX)
ROAD_RX = r'^road (?P<origin>{0}) (?P<destination>{0}) (?P<rate>{1})$'.format(INT_RX, FLOAT_RX)
BOARDS_RATE_RX = r'^board ({0})$'.format(FLOAT_RX)
DISEMBARKS_RATE_RX = r'^disembarks ({0})$'.format(FLOAT_RX)
DEPARTS_RATE_RX = r'^departs ({0})$'.format(FLOAT_RX)
NEW_PASSENGERS_RATE_RX = r'^new passengers ({0})$'.format(FLOAT_RX)
STOP_TIME_RX = r'^stop time ({0})$'.format(FLOAT_RX)
IGNORE_WARN_RX = r'^ignore warnings$'
OPTIMIZE_RX = r'^optimise parameters$'
NEWLINE_RX = r'^\n$'
COMMENT_RX = r'^#.*\n$'


class InputParser:
    """
    Object that is responsible for creating the network from the input file.
    """

    def __init__(self, filename=None):
        self.filename = filename
        self.network = Network()

    def parse_file(self):
        if self.filename is None:
            raise Exception("No input file specified!")
        with open(self.filename) as f:
            line_no = 1
            for line in f:
                self.parse_line(line.rstrip('\n'))  # get rid of newline
                line_no += 1
        # TODO:Finished parsing - do stuff like validate
        return self.network

    def parse_line(self, line):
        """
        Function that parses the line and calls an appropriate method
        """
        if self.rxmatch(ROUTE_RX, line):
            # TODO: Have to make this nicer - not dynamic enough!
            self.line_params['stop_ids'] = map(int, self.line_params['stop_ids'].split(' '))
            self.line_params['route_id'] = int(self.line_params['route_id'])
            self.line_params['bus_count'] = int(self.line_params['bus_count'])
            self.line_params['bus_capacity'] = int(self.line_params['bus_capacity'])
            self.network.add_route(**self.line_params)
        elif self.rxmatch(ROAD_RX, line):
            self.network.add_road(**self.line_params)
        elif self.rxmatch(BOARDS_RATE_RX, line):
            # SET BOARDS RATE
            pass
        elif self.rxmatch(DISEMBARKS_RATE_RX, line):
            # SET DISEMBARKS RATE
            pass
        elif self.rxmatch(DEPARTS_RATE_RX, line):
            # SET DEPARTS RATE
            pass
        elif self.rxmatch(NEW_PASSENGERS_RATE_RX, line):
            # SET NEW PASSENGERS RATE
            pass
        elif self.rxmatch(STOP_TIME_RX, line):
            # SET STOP TIME
            pass
        elif self.rxmatch(IGNORE_WARN_RX, line):
            # SET IGNORE WARNINGS
            pass
        elif self.rxmatch(OPTIMIZE_RX, line):
            # SET OPTIMIZE
            pass
        elif self.rxmatch(NEWLINE_RX, line) or self.rxmatch(COMMENT_RX, line):
            return  # ignore empty lines and comments

        # raise Exception('Invalid input on line {} of file {}'.format(line_no, self.line_no))

    def rxmatch(self, pattern, string):
        """
        Helper function for matching regular expressions.
        """
        match = re.match(pattern, string)
        if match:
            self.line_params = match.groupdict()
            if not self.line_params:
                self.line_params = match.group()
        return match

