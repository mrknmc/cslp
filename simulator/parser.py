import re

from collections import defaultdict
from models import Network


INT_RX = r'\d+'
FLOAT_RX = r'(\d+(\.\d*)?|\.\d+)'
NEWLINE_COMMENT_RX = r'^(\n|#.*\n)$'  # matches newline or a comment
INT_LIST_RX = r'{0}( {0})*'.format(INT_RX)
FLOAT_LIST_RX = r'{0}( {0})*'.format(FLOAT_RX)


def splitter(ftype, sort=False):
    """'1 2 3' -> [1, 2, 3]"""
    if sort:
        return lambda a: sorted(map(ftype, str.split(a, ' ')))
    else:
        return lambda a: map(ftype, str.split(a, ' '))


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
    'ex_bus_counts': splitter(int, sort=True),  # this sorted -> avoid removing buses
    'ex_caps': splitter(int)
}


EX_ROAD_RX = r' '.join([
    r'^road (?P<orig>{0}) (?P<dest>{0})',
    r'((?P<rate>{1})|experiment (?P<ex_rates>{2}))$'
]).format(INT_RX, FLOAT_RX, FLOAT_LIST_RX)

EX_ROAD_TYPES = {
    'orig': int,
    'dest': int,
    'rate': float,
    'ex_rates': splitter(float)
}


EX_RATES_RX = (
    ('boards', r'^board ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('disembarks', r'^disembarks ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('departs', r'^departs ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('new_passengers', r'^new passengers ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
)

EX_RATES_TYPES = {
    'ex_rates': splitter(float),
    'rate': float
}


STOP_TIME_RX = r'^stop time (?P<stop_time>{0})$'.format(FLOAT_RX)
IGNORE_WARN_RX = r'^ignore warnings$'
OPTIMIZE_RX = r'^optimise parameters$'


def parse_file(filename):
    """
    """
    network = Network()
    experimental_mode = False
    params = {}
    rates = {}
    experiments = {
        'bus_count': defaultdict(list),
        'cap': defaultdict(list),
        'rates': {
            'boards': [],
            'disembarks': [],
            'departs': [],
            'new_passengers': []
        }
    }
    with open(filename, 'r') as f:
        for line_no, line in enumerate(f, start=1):

            if rxmatch(NEWLINE_COMMENT_RX, line):
                continue  # ignore empty lines and comments

            line = line.rstrip('\n')  # get rid of newline

            match = rxmatch(EX_ROUTE_RX, line, fdict=EX_ROUTE_TYPES)
            if match:
                route_id = match['route_id']
                for name, ex_name in (('bus_count', 'ex_bus_counts'), ('cap', 'ex_caps')):
                    ex_param_lst = match[ex_name]
                    if ex_param_lst:
                        # Experiments - add every value
                        match[name] = ex_param_lst[0]
                        experimental_mode = True
                        for ex_param in ex_param_lst:
                            experiments[name][route_id].append(ex_param)
                    else:
                        # Only one value
                        experiments[name][route_id].append(match[name])

                network.add_route(**match)
                continue

            match = rxmatch(EX_ROAD_RX, line, fdict=EX_ROAD_TYPES)
            if match:
                orig = match['orig']
                dest = match['dest']
                ex_rates = match['ex_rates']
                if ex_rates:
                    experimental_mode = True
                    rates[orig, dest] = ex_rates[0]
                    # Experiments - add every value
                    experiments['rates'][(orig, dest)] = []
                    for ex_rate in ex_rates:
                        experiments['rates'][orig, dest].append(ex_rate)
                else:
                    # Only one value
                    experiments['rates'][orig, dest] = [match['rate']]
                    rates[orig, dest] = match['rate']
                continue

            for name, rate_rx in EX_RATES_RX:
                match = rxmatch(rate_rx, line, fdict=EX_RATES_TYPES)
                if match:
                    ex_rates = match['ex_rates']
                    if ex_rates:
                        experimental_mode = True
                        rates[name] = ex_rates[0]
                        # Experiments - add every value
                        for ex_rate in ex_rates:
                            experiments['rates'][name].append(ex_rate)
                    else:
                        # Only one value
                        experiments['rates'][name].append(match['rate'])
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

            raise Exception(
                'Invalid input on line {0} of file {1}:\n{2!r}'.format(line_no, filename, line)
            )

    params['experimental_mode'] = experimental_mode

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
