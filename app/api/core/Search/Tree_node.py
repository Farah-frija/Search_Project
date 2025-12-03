# Search/node.py

class Node:
    """Node in the search tree"""
    
    def __init__(self, state, parent=None, action=None, path_cost=0, depth=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action  # "up", "down", "tunnel", etc.
        self.path_cost = path_cost  # g(n)
        self.depth = depth
        self.heuristic = heuristic  # h(n)
    
    def __lt__(self, other):
        """For priority queue comparison"""
        return (self.path_cost + self.heuristic) < (other.path_cost + other.heuristic)
    
    def __repr__(self):
        return f"Node(state={self.state}, cost={self.path_cost}, h={self.heuristic})"
    
    def get_path(self):
        """Returns the sequence of actions from root to this node"""
        if self.parent is None:
            return []
        return self.parent.get_path() + [self.action]
    
    def get_path_with_states(self):
        """Returns list of states visited"""
        if self.parent is None:
            return [self.state]
        return self.parent.get_path_with_states() + [self.state]