

struct Bus {
    route: Route,
    bus_id: uint,
    cur_stop: uint,
    // pax_dests: Counter,
    road_rate: f64
}


impl Bus {

    pub fn new(route: Route, bus_id: uint) -> Bus {
        Bus {
            route: route,
            bus_id: bus_id,
            cur_stop: bus_id % route.stops.len(),
            // pax_dests: empty Counter
            road_rate: -1.0
        }
    }

    pub fn in_motion(&self) -> bool {
        self.road_rate != -1.0
    }

    pub fn stop(&self) -> Stop {
        self.route.get_stop(self.cur_stop)
    }

    pub fn departure_ready(&self) -> bool {
        self.disembarks() == 0 && (self.full(0) || self.boards().is_empty())
    }

    pub fn is_head(&self) -> bool {
        *self == self.stop().get_head()
    }

    pub fn disembarks(&self) -> int {
        self.pax_dests[self.stop().stop_id]
    }

    pub fn boards(&self) -> Vec<(int, int)> {
        // add code here
    }

    pub fn next_stop(&self) -> int {
        // add code here
    }

    pub fn pax_count(&self) -> int {
        // add code here
    }

    pub fn board(&self) {
        // add code here
    }

    pub fn disembark(&self) {
        // add code here
    }

    pub fn arrive(&self) {
        // add code here
    }

    pub fn full(&self, offset: int) -> bool {
        // add code here
    }

    pub fn satisfies(&self, dest: int) -> bool {
        // add code here
    }

}

impl Eq for Bus {
    fn eq(&self, other: &Bus) -> bool {
        self.bus_id == other.bus_id
    }
}


struct Route {
    route_id: uint,
    stops: ~[Stop],
    bus_count: uint,
    capacity: uint
}

impl Route {

    pub fn get_stop(&self, pos: uint) -> Stop {
        // add code here
    }

}


struct Stop {
    stop_id: uint,
    bus_queue: ~[Bus],
    // pax_dests: counter,
}

impl Stop {

    pub fn get_head(&self) -> Bus {
        self.bus_queue[0]
    }

    pub fn queue_length(&self) -> int {
        // add code here
    }

    pub fn pax_count(&self) -> int {
        // add code here
    }

}

fn main() {
    print!("Hello World!")
}
