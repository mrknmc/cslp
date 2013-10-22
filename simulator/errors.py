

class BusRoadStopConflict(Exception):

    def __repr__(self):
        return 'The bus cannot be on road and on a bus stop at the same time'
