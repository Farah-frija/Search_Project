import Edge


class TrafficData:
    def __init__(self):
        self.edges = {}  # Edge -> traffic

    def add_edge(self, pos1, pos2, traffic):
        self.edges[Edge(pos1, pos2)] = traffic

    def is_blocked(self, pos1, pos2):
        edge = Edge(pos1, pos2)
        return self.edges.get(edge, 1) == 0  # default to not blocked if not specified? Careful.