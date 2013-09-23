import unittest

from simulator.models import Network, Route


class TestNetwork(unittest.TestCase):

    def setUp(self):
        self.network = Network()


if __name__ == '__main__':
    unittest.main()
