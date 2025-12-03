class Edge:
    def __init__(self, pos1, pos2):
        # Store in sorted order for consistency (undirected)
        self.pos1 = min(pos1, pos2, key=lambda p: (p.x, p.y))
        self.pos2 = max(pos1, pos2, key=lambda p: (p.x, p.y))

    def __eq__(self, other):
        return (self.pos1 == other.pos1 and self.pos2 == other.pos2) or \
               (self.pos1 == other.pos2 and self.pos2 == other.pos1)

    def __hash__(self):
        return hash((self.pos1, self.pos2))

    def __repr__(self):
        return f"[{self.pos1}->{self.pos2}]"

    def connects(self, pos):
        return pos == self.pos1 or pos == self.pos2

    def other_end(self, pos):
        if pos == self.pos1:
            return self.pos2
        elif pos == self.pos2:
            return self.pos1
        else:
            return None