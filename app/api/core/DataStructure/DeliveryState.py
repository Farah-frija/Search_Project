class DeliveryState:
    def __init__(self, current_pos, target_pos, cost_so_far=0):
        self.current_pos = current_pos
        self.target_pos = target_pos
        self.cost_so_far = cost_so_far

    def __eq__(self, other):
        return (self.current_pos == other.current_pos and
                self.target_pos == other.target_pos)

    def __hash__(self):
        return hash((self.current_pos, self.target_pos))

    def is_goal(self):
        return self.current_pos == self.target_pos

    def __repr__(self):
        return f"State(pos={self.current_pos}, target={self.target_pos}, cost={self.cost_so_far})"