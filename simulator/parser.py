import re

from models import Network


INT_RX = r'\d+'
FLOAT_RX = r'(\d+(\.\d*)?|\.\d+)'
NEWLINE_COMMENT_RX = r'^(\n|#.*\n)$'  # matches newline or a comment
INT_LIST_RX = r'{0}( {0})*'.format(INT_RX)
FLOAT_LIST_RX = r'{0}( {0})*'.format(FLOAT_RX)


def splitter(ftype):
    """'1 2 3' -> [1, 2, 3]"""
    return lambda a: map(ftype, str.split(a, ' '))


ROUTE_RX = r' '.join([
    r'^route (?P<route_id>{0})',
    r'stops (?P<stop_ids>{1})',
    r'buses (?P<bus_count>{0})',
    r'capacity (?P<cap>{0})$'
]).format(INT_RX, INT_LIST_RX)

ROUTE_TYPES = {
    'route_id': int,
    'stop_ids': splitter(int),
    'bus_count': int,
    'cap': int,
}


EX_ROUTE_RX = r' '.join([
    r'^route (?P<route_id>{0})',
    r'stops (?P<stop_ids>{1})',
    r'buses ((?P<bus_count>{0})|experiment (?P<ex_bus_counts>{1}))',
    r'capacity ((?P<cap>{0})|experiment (?P<ex_caps>{1}))$'
]).format(INT_RX, INT_LIST_RX)

EX_ROUTE_TYPES = {
    'route_id': int,
    'stop_ids': splitter(int),
    'bus_count': int,
    'cap': int,
    'ex_bus_counts': splitter(int),
    'ex_caps': splitter(int)
}


EX_ROAD_RX = r' '.join([
    r'^road (?P<orig>{0}) (?P<dest>{0})',
    # r'(?P<rate>{1})$'
    r'((?P<rate>{1})|experiment (?P<ex_rates>{2}))$'
]).format(INT_RX, FLOAT_RX, FLOAT_LIST_RX)

EX_ROAD_TYPES = {
    'orig': int,
    'dest': int,
    'rate': float,
    'ex_rates': splitter(float)
}


ROAD_RX = r' '.join([
    r'^road (?P<orig>{0}) (?P<dest>{0})',
    r'experiment (?P<rate>{1})$'
]).format(INT_RX, FLOAT_RX)

ROAD_TYPES = {
    'orig': int,
    'dest': int,
    'rate': float,
}


EX_RATES_RX = (
    ('boards', r'^board ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('disembarks', r'^disembarks ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('departs', r'^departs ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('new_passengers', r'^new passengers ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
)


RATES_RX = (
    r'^board (?P<boards>{0})$'.format(FLOAT_RX),
    r'^disembarks (?P<disembarks>{0})$'.format(FLOAT_RX),
    r'^departs (?P<departs>{0})$'.format(FLOAT_RX),
    r'^new passengers (?P<new_passengers>{0})$'.format(FLOAT_RX),
)


STOP_TIME_RX = r'^stop time (?P<stop_time>{0})$'.format(FLOAT_RX)
IGNORE_WARN_RX = r'^ignore warnings$'
OPTIMIZE_RX = r'^optimise parameters$'


def parse_file(filename):
    """
    """
    network = Network()
    params = {}
    rates = {}
    experiments = {
        'bus_count': {},
        'cap': {},
        'road': {},
        'board': {},
        'disembarks': {},
        'departs': {},
        'new_passengers': {}
    }
    with open(filename, 'r') as f:
        for line_no, line in enumerate(f, start=1):
            line = line.rstrip('\n')  # get rid of newline

            # EXPERIMENTAL ROUTE
            match = rxmatch(EX_ROUTE_RX, line, fdict=EX_ROUTE_TYPES)
            if match:
                bus_counts = match['ex_bus_counts']
                if bus_counts:
                    match['bus_count'] = bus_counts.pop(0)
                    # put the rest of the array in experiments
                    route_id = match['route_id']
                    experiments['bus_count'][route_id] = bus_counts

                ex_caps = match['ex_caps']
                if ex_caps:
                    match['cap'] = ex_caps.pop(0)
                    # put the rest of the array in experiments
                    route_id = match['route_id']
                    experiments['cap'][route_id] = ex_caps

                network.add_route(**match)
                continue

            # EXPERIMENTAL ROAD
            match = rxmatch(EX_ROAD_RX, line, fdict=EX_ROAD_TYPES)
            if match:
                orig = match['orig']
                dest = match['dest']
                ex_rates = match['ex_rates']
                if ex_rates:
                    match['rate'] = ex_rates.pop(0)
                    # put the rest of the array in experiments
                    experiments['road'][orig, dest] = ex_rates

                rates[orig, dest] = match['rate']
                continue

            # EXPERIMENTAL RATES
            for name, rate_rx in EX_RATES_RX:
                match = rxmatch(rate_rx, line, ftype=float)
                if match:
                    ex_rates = match['ex_rates']
                    if ex_rates:
                        match['rate'] = ex_rates.pop(0)
                        # put the rest of the array in experiments
                        experiments[name] = ex_rates

                    rates[name] = match['rate']
                    break
            if match:
                continue

            match = rxmatch(STOP_TIME_RX, line, ftype=float)
            if match:
                params.update(**match)
                continue

            if rxmatch(IGNORE_WARN_RX, line):
                params['ignore_warn'] = True
                continue

            if rxmatch(OPTIMIZE_RX, line):
                params['optimize'] = True
                continue

            if rxmatch(NEWLINE_COMMENT_RX, line):
                continue  # ignore empty lines and comments

            raise Exception(
                'Invalid input on line {0} of file {1}:\n{2!r}'.format(line_no, filename, line)
            )

    return network, rates, params, experiments


def rxmatch(pattern, string, ftype=None, fdict=None):
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
        for key, val in groupdict.iteritems():
            if val is None:
                continue
            groupdict[key] = ftype(val)
    elif fdict:
        for key, val in groupdict.iteritems():
            if val is None:
                continue
            groupdict[key] = fdict[key](val)
    return groupdict
