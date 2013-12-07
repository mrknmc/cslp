from random import choice, random
from math import log10
from events import log, EventMap
from parser import parse_file
from collections import Counter


class World(object):

    def __init__(self, filename=None):
        """
        Initialize the world.
        """
        self.time = 0.0
        if not filename:
            return  # mainly for testing - init the world add params later
        network, rates, params = parse_file(filename)
        self.network = network
        self.event_map = EventMap()
        self.rates = rates
        self.total_rate = rates['new_passengers']  # new passengers is always available

        # add buses to departs and increment total_rate
        for stop in network.stops.itervalues():
            self.event_map.departs.extend(stop.bus_queue)
            self.total_rate += len(stop.bus_queue) * rates['departs']

        # Set all flags
        for key, val in params.iteritems():
            setattr(self, key, val)

    def dequeue_bus(self, bus):
        """
        The first bus departs from the queue.
        """
        cur_stop = bus.stop
        cur_stop.bus_queue.remove(bus)
        next_stop = bus.route.next_stop(cur_stop.stop_id)  # set next stop
        bus.road_rate = self.rates[cur_stop.stop_id, next_stop.stop_id]
        bus.stop = next_stop

    def gen_pax(self):
        """
        Generates a passenger on the network.
        """
        orig = choice(self.network.stops.values())

        dests = []
        for route in self.network.routes.itervalues():
            try:
                idx = route.stops.index(orig)
                dests.extend(route.stops[:idx])
                dests.extend(route.stops[idx+1:])
            except ValueError:
                continue

        dest = choice(dests)
        return dict(orig=orig, dest=dest)

    def update(self, event_type, **kwargs):
        rates = self.rates
        total_rate = self.total_rate
        e_map = self.event_map

        if event_type == 'boards':
            bus = kwargs['bus']
            dest_id = kwargs['dest']
            stop = bus.stop

            # Update the world
            stop.pax_dests[dest_id] -= 1  # no longer on the stop
            bus.pax_dests[dest_id] += 1  # now on the bus

            if bus.full():
                # No one can board this bus anymore - it's full
                bus_boards = sum(e_map.boards[bus].itervalues())
                total_rate -= bus_boards * rates['boards']
                del(e_map.boards[bus])

            for bus in stop.bus_queue:
                if bus.satisfies(dest_id):
                    # This person can not board any buses anymore
                    total_rate -= rates['boards']
                    e_map.boards[bus][dest_id] -= 1
                    # Bus may be ready for departure
                    if bus.departure_ready:
                        total_rate += rates['departs']
                        e_map.departs.append(bus)

        elif event_type == 'disembarks':
            bus = kwargs['bus']
            stop_id = bus.stop.stop_id

            # Update the world
            bus.pax_dests[stop_id] -= 1  # no longer on the bus

            # Event not available anymore
            total_rate -= rates['disembarks']
            if bus.disembarks == 0:
                e_map.disembarks.remove(bus)

            # If the bus was full then people can now board it
            if bus.full(offset=1):
                bus_boards = Counter(dict(bus.boards))
                total_rate += sum(bus_boards.itervalues()) * rates['boards']
                e_map.boards[bus] = bus_boards

            # If no one else wants to disembark or embark then it is departure ready
            if bus.departure_ready:
                total_rate += rates['departs']
                e_map.departs.append(bus)

        elif event_type == 'departs':
            bus = kwargs['bus']

            # Update the world
            self.dequeue_bus(bus)

            # Event is not available anymore
            total_rate -= rates['departs']
            e_map.departs.remove(bus)

            # How it affects other events
            total_rate += bus.road_rate
            e_map.arrivals.append(bus)

        elif event_type == 'arrivals':
            bus = kwargs['bus']
            stop = bus.stop
            road_rate = bus.road_rate

            # Update the world
            stop.bus_queue.append(bus)  # on the stop now
            bus.road_rate = None  # no longer on the road

            # Event not available anymore
            e_map.arrivals.remove(bus)
            total_rate -= road_rate

            # People on the stop can now board the bus
            bus_boards = Counter(dict(bus.boards))
            if bus_boards:
                # Some people want to board the bus
                total_rate += sum(bus_boards.itervalues()) * rates['boards']
                e_map.boards[bus] = bus_boards
            elif bus.departure_ready:
                # No one wants to board the bus - it can depart
                total_rate += rates['departs']
                e_map.departs.append(bus)

            # People on the bus can now disembark it
            bus_disembarks = bus.disembarks
            # print bus_disembarks
            total_rate += bus_disembarks * rates['disembarks']
            if bus_disembarks and bus not in e_map.disembarks:
                e_map.disembarks.append(bus)
        else:
            # Update the world
            orig, dest = kwargs['orig'], kwargs['dest']
            orig.pax_dests[dest.stop_id] += 1

            # The person can board some buses on the origin stop
            dest_id = dest.stop_id
            for bus in orig.bus_queue:
                if bus.satisfies(dest_id):
                    # Bus can not depart now if it satisfies the destination
                    if bus in e_map.departs:
                        total_rate -= rates['departs']
                        e_map.departs.remove(bus)
                    total_rate += rates['boards']
                    e_map.boards[bus][dest_id] += 1

        self.total_rate = total_rate
        self.event_map = e_map

    def choose_event(self):
        """
        Chooses an event based on the last event.
        """
        rand = random() * self.total_rate

        for bus, dest, count in self.event_map.gen_boards():
            rand -= count * self.rates['boards']
            if rand < 0:
                return 'boards', dict(dest=dest, bus=bus)

        for bus in self.event_map.disembarks:
            rand -= bus.disembarks * self.rates['disembarks']
            if rand < 0:
                return 'disembarks', dict(bus=bus)

        for bus in self.event_map.departs:
            rand -= self.rates['departs']
            if rand < 0:
                return 'departs', dict(dest=bus.stop, bus=bus)

        for bus in self.event_map.arrivals:
            rand -= bus.road_rate
            if rand < 0:
                return 'arrivals', dict(bus=bus)

        return 'new_passengers', self.gen_pax()

    def sample_delay(self):
        """
        Return a sample delay based on the total rate.
        """
        mean = 1 / self.total_rate
        return -mean * log10(random())

    def validate(self):
        """
        If any of the needed rates was not set the simulation is not valid.

        Next, validate the network.
        """
        if any([
            self.boards is None,
            self.disembarks is None,
            self.departs is None,
            self.new_passengers is None,
            self.stop_time is None
        ]):
            raise Exception("The simulation is not valid.")
        self.network.validate()

    def start(self):
        """
        Validate and then start the run loop.
        """
        self.run()

    def run(self):
        """
        Run the simulation until world explodes.
        """
        while self.time <= self.stop_time:
            delay = self.sample_delay()
            event_type, kwargs = self.choose_event()
            self.update(event_type, **kwargs)
            log(event_type, time=self.time, **kwargs)
            self.time += delay
