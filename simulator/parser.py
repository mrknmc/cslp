import re

from collections import defaultdict
from simulator.errors import InputError, InputWarning
from simulator.models import Network
from simulator.formats import NEWLINE_COMMENT_RX, ROUTE_RX, ROUTE_TYPES, \
    ROAD_RX, ROAD_TYPES, RATES_RX, RATES_TYPES, STOP_TIME_RX, \
    IGNORE_WARN_RX, OPTIMIZE_RX


def parse_lines(file, filename):
    network = Network()
    params = {'optimise': False, 'ignore_warn': False, 'experimental_mode': False}
    rates = {}
    experiments = {
        'routes': defaultdict(lambda: defaultdict(int)),
        'rates': {}
    }
    for line_no, line in enumerate(file, start=1):

        # ignore empty lines and comments
        if rxmatch(NEWLINE_COMMENT_RX, line):
            continue

        line = line.rstrip('\n')  # get rid of newline

        match = rxmatch(ROUTE_RX, line, fdict=ROUTE_TYPES)
        if match:
            route_id = match['route_id']
            for name, ex_name in (('bus_count', 'ex_bus_counts'), ('cap', 'ex_caps')):
                ex_param_lst = match[ex_name]
                if ex_param_lst:
                    # Experiments - add every value
                    match[name] = ex_param_lst[0]
                    params['experimental_mode'] = True
                    experiments['routes'][route_id][name] = ex_param_lst

            network.add_route(**match)
            continue

        match = rxmatch(ROAD_RX, line, fdict=ROAD_TYPES)
        if match:
            orig = match['orig']
            dest = match['dest']
            ex_rates = match['ex_rates']
            if ex_rates:
                params['experimental_mode'] = True
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
                    params['experimental_mode'] = True
                    rates[name] = ex_rates[0]
                    # Experiments - add every value
                    experiments['rates'][name] = ex_rates
                else:
                    # Only one value
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
            params['optimise'] = True
            continue

        raise InputError(
            'Invalid input on line {0} of file {1}:\n{2!r}'.format(line_no, filename, line)
        )

    return network, rates, params, experiments


def parse_file(filename):
    with open(filename, 'r') as f:
        return parse_lines(f, filename)


def rxmatch(pattern, string, ftype=None, fdict=None):
    """
    Helper function for matching regular expressions. Will convert matched
    groups into correct type based on the ftype parameter.

    Returns a dictionary if there are any params, True if not and False if
    there is no match.
    """
    match = re.match(pattern, string)
    if match is None:
        return False
    groupdict = match.groupdict()
    if not groupdict:
        return True

    if ftype:
        for key, val in groupdict.iteritems():
            if val:
                groupdict[key] = ftype(val)
    elif fdict:
        for key, val in groupdict.iteritems():
            if val:
                groupdict[key] = fdict[key](val)
    return groupdict
