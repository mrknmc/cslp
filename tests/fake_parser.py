from simulator.parser import *

from io import BytesIO


def parse_file(input_str):
    """
    """
    network = Network()
    params = {}
    with BytesIO(input_str) as f:
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
                    params.update(**match)
                    break
            if match:
                continue

            if rxmatch(IGNORE_WARN_RX, line):
                params['ignore_warn'] = True
                continue

            if rxmatch(OPTIMIZE_RX, line):
                params['optimize'] = True
                continue

            if rxmatch(NEWLINE_COMMENT_RX, line):
                continue  # ignore empty lines and comments

            raise Exception('Invalid input on line {0} of test file:\n{1!r}'.format(
                line_no,
                line
            ))

    return network, params
