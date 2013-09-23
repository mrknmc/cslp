import re

from models import Network


FLOAT_RX = r'\d*(.\d*)?'

ROUTE_RX = r'^route (?P<route_id>\d+) stops (?P<stop_ids>\d+( \d+)*) buses (?P<bus_count>\d+) capacity (?P<bus_capacity>\d+)$',
ROAD_RX = r'^road (?P<origin>\d+) (?P<destination>\d+) (?P<rate>{float})$'.format(float=FLOAT_RX),
BOARDS_RATE_RX = r'^board ({float})$'.format(float=FLOAT_RX),
DISEMBARKS_RATE_RX = r'^disembarks {float}$'.format(float=FLOAT_RX),
DEPARTS_RATE_RX = r'^departs {float}$'.format(float=FLOAT_RX),
NEW_PASSENGERS_RATE_RX = r'^new passengers {float}$'.format(float=FLOAT_RX),
STOP_TIME_RX = r'^stop time {float}$'.format(float=FLOAT_RX),
IGNORE_WARN_RX = r'^ignore warnings$',
OPTIMIZE_RX = r'^optimise parameters$',
NEWLINE_RX = r'^\n$',
COMMENT_RX = r'^#.*\n$',


class InputParser:
    """
    Object that is responsible for creating the network from the input file.
    """

    def __init__(self, filename=None):
        self.filename = filename
        self.network = Network()

    def parseFile(self):
        if self.filename is None:
            raise Exception("No input file specified!")
        with open(self.filename) as f:
            for line in f:
                self.parse_line(line)
        # Finished parsing - do stuff

    def parse_line(self, line):
        """
        Function that parses the line and calls an appropriate method
        """
        if re.match(ROUTE_RX, line):
            self.network.add_route(**self.line_params)
        elif re.match(ROAD_RX, line):
            self.network.add_road(**self.line_params)
        elif re.match(BOARDS_RATE_RX, line):
            # SET BOARDS RATE
            pass
        elif re.match(DISEMBARKS_RATE_RX, line):
            # SET DISEMBARKS RATE
            pass
        elif re.match(DEPARTS_RATE_RX, line):
            # SET DEPARTS RATE
            pass
        elif re.match(NEW_PASSENGERS_RATE_RX, line):
            # SET NEW PASSENGERS RATE
            pass
        elif re.match(STOP_TIME_RX, line):
            # SET STOP TIME
            pass
        elif re.match(IGNORE_WARN_RX, line):
            # SET IGNORE WARNINGS
            pass
        elif re.match(OPTIMIZE_RX, line):
            # SET OPTIMIZE
            pass
        elif re.match(NEWLINE_RX, line):
            return
        elif re.match(COMMENT_RX, line):
            return

        raise Exception('Line number blah-blah not recognized as valid input')

    def rxmatch(self, pattern, string):
        """
        Helper function for matching regular expressions.
        """
        match = re.match(pattern, string)
        self.line_params = match.groupdict()
        if not self.line_params:
            self.line_params = match.group()
        return match

