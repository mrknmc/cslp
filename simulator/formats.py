
def splitter(ftype, sort=False):
    """
    '1 2 3' -> [1, 2, 3]
    """
    return lambda s: map(ftype, s.split(' '))


#####################################################################
### REGULAR EXPRESSION FORMATS
#####################################################################

INT_RX = r'\d+'  # (123|8|09)
FLOAT_RX = r'(\d+(\.\d*)?|\.\d+)'  # (2.3|0.9|.6)
NEWLINE_COMMENT_RX = r'^(\n|#.*\n)$'  # newline or a comment
INT_LIST_RX = r'{0}( {0})*'.format(INT_RX)  # 3 5 12 9
FLOAT_LIST_RX = r'{0}( {0})*'.format(FLOAT_RX)  # 1.1 0.4 .3

STOP_TIME_RX = r'^stop time (?P<stop_time>{0})$'.format(FLOAT_RX)
IGNORE_WARN_RX = r'^ignore warnings$'
OPTIMIZE_RX = r'^optimise parameters$'


ROUTE_RX = r' '.join([
    r'^route (?P<route_id>{0})',
    r'stops (?P<stop_ids>{1})',
    r'buses ((?P<bus_count>{0})|experiment (?P<ex_bus_counts>{1}))',
    r'capacity ((?P<cap>{0})|experiment (?P<ex_caps>{1}))$'
]).format(INT_RX, INT_LIST_RX)

# types for the routes regex above
ROUTE_TYPES = {
    'route_id': int,
    'stop_ids': splitter(int),
    'bus_count': int,
    'cap': int,
    'ex_bus_counts': splitter(int),
    'ex_caps': splitter(int)
}


ROAD_RX = r' '.join([
    r'^road (?P<orig>{0}) (?P<dest>{0})',
    r'((?P<rate>{1})|experiment (?P<ex_rates>{2}))$'
]).format(INT_RX, FLOAT_RX, FLOAT_LIST_RX)

# types for the road regex above
ROAD_TYPES = {
    'orig': int,
    'dest': int,
    'rate': float,
    'ex_rates': splitter(float)
}


RATES_RX = (
    ('board', r'^board ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('disembarks', r'^disembarks ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('departs', r'^departs ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
    ('new_passengers', r'^new passengers ((?P<rate>{0})|(experiment (?P<ex_rates>{1})))$'.format(FLOAT_RX, FLOAT_LIST_RX)),
)

# types for the rates regexes above
RATES_TYPES = {
    'ex_rates': splitter(float),
    'rate': float
}


#####################################################################
### EVENT FORMATS
#####################################################################

EVENTS = {
    'arrivals': 'Bus {bus} arrives at stop {bus.stop} at time {time}',
    'departs': 'Bus {bus} leaves stop {dest} at time {time}',
    'board': 'Passenger boards bus {bus} at stop {bus.stop} with destination {dest} at time {time}',
    'disembarks': 'Passenger disembarks bus {bus} at stop {bus.stop} at time {time}',
    'new_passengers': 'A new passenger enters at stop {orig} with destination {dest} at time {time}'
}


EVENT_COLOURS = {
    'arrivals': 'blue',
    'departs': 'red',
    'board': 'yellow',
    'disembarks': 'cyan',
    'new_passengers': 'magenta'
}


#####################################################################
### EXPERIMENT PARAMETER FORMATS
#####################################################################

EXPERIMENTS_PARAMS = {
    'route': 'route {route_id} stops {stops} buses {bus_count} capacity {cap}',
    'road': 'road {0} {1}',
    'rate': '{name} {rate}'
}


#####################################################################
### ANALYSIS FORMATS
#####################################################################

ANALYSIS = {
    'missed_pax': {
        'route': 'number of missed passengers route {0} {1}',
        'stop': 'number of missed passengers stop {0} {1}',
        'total': 'number of missed passengers {}'
    },
    'avg_pax': {
        'bus': 'average passengers bus {0} {1}',
        'route': 'average passengers route {0} {1}',
        'total': 'average passengers {}'
    },
    'avg_qtime': {
        'stop': 'average queueing at stop {0} {1}',
        'total': 'average queueing at all stops {}'
    },
    'avg_wtime': {
        'route': 'average waiting passengers on route {0} {1}',
        'stop': 'average waiting passengers at stop {0} {1}',
        'total': 'average waiting passengers {}',
    }
}

