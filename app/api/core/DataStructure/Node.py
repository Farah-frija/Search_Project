class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action  # "up", "down", "tunnel", etc.
        self.path_cost = path_cost
        self.depth = depth

    def __lt__(self, other):
        return self.path_cost < other.path_cost  # For priority queue

    def __repr__(self):
        return f"Node({self.state}, action={self.action}, cost={self.path_cost})"