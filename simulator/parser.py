import re

from collections import defaultdict
from models import Network
from formats import NEWLINE_COMMENT_RX, ROUTE_RX, ROUTE_TYPES, ROAD_RX, \
    ROAD_TYPES, RATES_RX, RATES_TYPES, STOP_TIME_RX, IGNORE_WARN_RX, OPTIMIZE_RX


def parse_file(filename):
    """
    """
    network = Network()
    experimental_mode = False
    params = {}
    rates = {}
    experiments = {
        'routes': defaultdict(lambda: defaultdict(int)),
        'rates': {}
    }
    with open(filename, 'r') as f:
        for line_no, line in enumerate(f, start=1):

            if rxmatch(NEWLINE_COMMENT_RX, line):
                continue  # ignore empty lines and comments

            line = line.rstrip('\n')  # get rid of newline

            match = rxmatch(ROUTE_RX, line, fdict=ROUTE_TYPES)
            if match:
                route_id = match['route_id']
                for name, ex_name in (('bus_count', 'ex_bus_counts'), ('cap', 'ex_caps')):
                    ex_param_lst = match[ex_name]
                    if ex_param_lst:
                        # Experiments - add every value
                        match[name] = ex_param_lst[0]
                        experimental_mode = True
                        experiments['routes'][route_id][name] = ex_param_lst

                network.add_route(**match)
                continue

            match = rxmatch(ROAD_RX, line, fdict=ROAD_TYPES)
            if match:
                orig = match['orig']
                dest = match['dest']
                ex_rates = match['ex_rates']
                if ex_rates:
                    experimental_mode = True
                    rates[orig, dest] = ex_rates[0]
                    # Experiments - add every value
                    experiments['rates'][orig, dest] = ex_rates
                else:
                    # Only one value
                    rates[orig, dest] = match['rate']

                continue

            for name, rate_rx in RATES_RX:
                match = rxmatch(rate_rx, line, fdict=RATES_TYPES)
                if match:
                    ex_rates = match['ex_rates']
                    if ex_rates:
                        experimental_mode = True
                        rates[name] = ex_rates[0]
                        # Experiments - add every value
                        # for ex_rate in ex_rates:
                        experiments['rates'][name] = ex_rates
                    else:
                        # Only one value
                        # experiments['rates'][name].append(match['rate'])
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
