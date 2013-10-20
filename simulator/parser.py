import re

from simulator.models import Network

INT_RX = r'\d+'
FLOAT_RX = r'(\d+(\.\d*)?|\.\d+)'
NEWLINE_COMMENT_RX = r'^(\n|#.*\n)$'  # matches newline or a comment

ROUTE_RX = r'^route (?P<route_id>{0}) stops (?P<stop_ids>{0}( {0})*) buses (?P<bus_count>{0}) capacity (?P<bus_capacity>{0})$'.format(INT_RX)
ROAD_RX = r'^road (?P<origin>{0}) (?P<destination>{0}) (?P<rate>{1})$'.format(INT_RX, FLOAT_RX)
RATES_RX = (
    r'^board (?P<board>{0})$'.format(FLOAT_RX),
    r'^disembarks (?P<disembarks>{0})$'.format(FLOAT_RX),
    r'^departs (?P<departs>{0})$'.format(FLOAT_RX),
    r'^new passengers (?P<new_passengers>{0})$'.format(FLOAT_RX),
    r'^stop time (?P<stop_time>{0})$'.format(FLOAT_RX),
)
IGNORE_WARN_RX = r'^ignore warnings$'
OPTIMIZE_RX = r'^optimise parameters$'

ROUTE_TYPES = {
    'route_id': int,
    'stop_ids': lambda a: map(int, str.split(a, ' ')),  # '1 2 3' -> [1, 2, 3]
    'bus_count': int,
    'bus_capacity': int
}

ROAD_TYPES = {
    'origin': int,
    'destination': int,
    'rate': float
}


def parse_file(filename):
    """
    """
    network = Network()
    rates = {}
    flags = {}
    with open(filename, 'r') as f:
        for line_no, line in enumerate(f, start=1):
            line = line.rstrip('\n')  # get rid of newline

            match = rxmatch(ROUTE_RX, line, ftype=ROUTE_TYPES)
            if match:
                network.add_route(**match)
                continue

            match = rxmatch(ROAD_RX, line, ftype=ROAD_TYPES)
            if match:
                network.add_road(**match)
                continue

            for rate_rx in RATES_RX:
                match = rxmatch(rate_rx, line, ftype=float)
                if match:
                    rates.update(**match)
                    continue

            if rxmatch(IGNORE_WARN_RX, line):
                flags['ignore_warn'] = True
                continue

            if rxmatch(OPTIMIZE_RX, line):
                flags['optimize'] = True
                continue

            if rxmatch(NEWLINE_COMMENT_RX, line):
                continue  # ignore empty lines and comments

            raise Exception('Invalid input on line {0} of file {1}'.format(line_no, filename))

    return network, rates, flags


def rxmatch(pattern, string, ftype=None):
    """
    Helper function for matching regular expressions. Will convert matched
    groups into correct type based on the ftype parameter.

    Returns a dictionary if there are any params, True if not and False if
    there is no match.
    """
    match = re.match(pattern, string)
    if not match:
        return False
    groupdict = match.groupdict()
    if not groupdict:
        return True
    if ftype:
        if isinstance(ftype, dict):
            for key, val in groupdict.iteritems():
                groupdict[key] = ftype[key](val)
        else:
            for key, val in groupdict.iteritems():
                groupdict[key] = ftype(val)
    return groupdict
