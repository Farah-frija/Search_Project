import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataStructure.Edge import Edge
class Grid:
    def __init__(self, m, n):
        self.m = m  # width
        self.n = n  # height
        self.stores = []          # list of Position
        self.customers = []       # list of Position
        self.traffic = {}         # Edge -> int (0 = blocked)
        self.tunnels = {}         # Position -> Position (bidirectional)

    def add_store(self, pos):
        self.stores.append(pos)

    def add_customer(self, pos):
        self.customers.append(pos)

    def set_traffic(self, pos1, pos2, level):
        edge = Edge(pos1, pos2)
        self.traffic[edge] = level

    def add_tunnel(self, entrance1, entrance2):
        self.tunnels[entrance1] = entrance2
        self.tunnels[entrance2] = entrance1

    def get_traffic_level(self, pos1, pos2):
        edge = Edge(pos1, pos2)
        return self.traffic.get(edge, None)  # None if not defined

    def is_blocked(self, pos1, pos2):
        traffic = self.get_traffic_level(pos1, pos2)
        return traffic == 0

    def get_tunnel_exit(self, pos):
        return self.tunnels.get(pos, None)