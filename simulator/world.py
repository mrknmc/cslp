from random import choice, random
from math import log10
from events import log, EventMap
from parser import parse_file


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
        if event_type == 'boards':
            bus = kwargs['bus']
            dest_id = kwargs['dest'].stop_id
            stop = bus.stop

            stop.pax_dests[dest_id] -= 1
            bus.pax_dests[dest_id] += 1

            for bus in stop.bus_queue:
                # Decrement boards destination count of all buses that satisfy dest
                if bus.satisfies(dest_id):
                    self.total_rate -= self.rates['boards']
                    self.event_map.boards[bus][dest_id] -= 1

            if bus.full():
                # Increment the total rate by rate of one departure
                self.total_rate += self.rates['departs']
                self.event_map.departs.append(bus)

                # Remove boarders of this bus - it's full
                bus_boards = self.event_map.boards[bus]
                self.total_rate -= sum(bus_boards.itervalues()) * self.rates['boards']
                del(self.event_map.boards[bus])

        elif event_type == 'disembarks':
            bus = kwargs['bus']
            stop_id = bus.stop.stop_id

            bus.pax_dests[stop_id] -= 1

            # Decrease the disembarks by one
            self.total_rate -= self.rates['disembarks']
            self.event_map.disembarks[bus][stop_id] -= 1

            # TODO: this is relying on the fact that world update happens AFTER event update
            if bus.full(offset=1):
                # Add boards if bus was full
                bus_boards = dict(bus.boards())
                self.total_rate -= sum(bus_boards.itervalues()) * self.rates['boards']
                self.event_map.boards[bus] = bus_boards

        elif event_type == 'departs':
            bus = kwargs['bus']

            self.dequeue_bus(bus)

            # The bus is no longer ready for departure
            self.total_rate -= self.rates['departs']
            self.event_map.departs.remove(bus)

            # The bus is now ready for arrival
            self.total_rate += bus.road_rate
            self.event_map.arrivals.append(bus)

        elif event_type == 'arrivals':
            bus = kwargs['bus']

            bus.stop.bus_queue.append(bus)
            self.total_rate -= bus.road_rate
            bus.road_rate = None

            # Update 'boarders'
            bus_boards = dict(bus.boards())
            self.total_rate += sum(bus_boards.itervalues()) * self.rates['boards']
            self.event_map.boards[bus] = bus_boards
            # Update 'disembarkers'
            bus_disembarks = dict(bus.disembarks())
            self.total_rate += sum(bus_disembarks.itervalues()) * self.rates['disembarks']
            self.event_map.disembarks[bus] = bus_disembarks
        else:
            # Passenger creation
            orig, dest = kwargs['orig'], kwargs['dest']
            orig.pax_dests[dest.stop_id] += 1
            # Update 'boarders'
            dest_id = dest.stop_id
            for bus in orig.bus_queue:
                if bus.satisfies(dest_id):
                    self.total_rate += self.rates['boards']
                    self.event_map.boards[bus][dest_id] += 1

    def choose_event(self):
        """
        Chooses an event based on the last event.
        """
        rand = random() * self.total_rate

        for bus, dest, count in self.event_map.gen_boards():
            rand -= count * self.rates['boards']
            if rand < 0:
                return 'boards', dict(stop=dest, bus=bus)

        for bus, dest, count in self.event_map.gen_disembarks():
            rand -= count * self.rates['disembarks']
            if rand < 0:
                return 'disembarks', dict(stop=dest, bus=bus)

        for bus in self.event_map.departs:
            rand -= self.rates['departs']
            if rand < 0:
                return 'departs', dict(bus=bus)

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
            log(event_type, time=self.time, **kwargs)
            print event_type
            self.update(event_type, **kwargs)
            self.time += delay
