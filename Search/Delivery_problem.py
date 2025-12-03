# Search/delivery_problem.py
from .Search_problem import SearchProblem
from DataStructure.Position import Position
from DataStructure.DeliveryState import DeliveryState
class DeliveryProblem(SearchProblem):
    """Concrete implementation for package delivery problem"""
    
    def __init__(self, grid, start_pos, goal_pos):
        """
        Args:
            grid: Grid object
            start_pos: Position of store (starting point)
            goal_pos: Position of customer (goal)
        """
        self.grid = grid
        self.start_pos = start_pos
        self.goal_pos = goal_pos
    
    def get_start_state(self):
        return DeliveryState(self.start_pos, self.goal_pos, 0)
    
    def is_goal_state(self, state):
        return state.current_pos == self.goal_pos
    
    def get_successors(self, state):
        """Get possible moves from current state"""
        successors = []
        current_pos = state.current_pos
        
        # Possible moves: up, down, left, right
        directions = [
            ("up", Position(0, -1)),
            ("down", Position(0, 1)),
            ("left", Position(-1, 0)),
            ("right", Position(1, 0))
        ]
        
        for action_name, delta in directions:
            new_x = current_pos.x + delta.x
            new_y = current_pos.y + delta.y
            new_pos = Position(new_x, new_y)
            
            # Check if within grid bounds
            if not (0 <= new_x < self.grid.m and 0 <= new_y < self.grid.n):
                continue
            
            # Check if road is blocked
            if self.grid.is_blocked(current_pos, new_pos):
                continue
            
            # Get traffic cost
            traffic = self.grid.get_traffic_level(current_pos, new_pos)
            if traffic is None:
                continue  # No traffic data for this segment
            
            # Create new state
            new_state = DeliveryState(new_pos, self.goal_pos, 
                                     state.cost_so_far + traffic)
            successors.append((new_state, action_name, traffic))
        
        # Check for tunnel
        tunnel_exit = self.grid.get_tunnel_exit(current_pos)
        if tunnel_exit:
            # Tunnel action
            tunnel_cost = current_pos.manhattan_distance(tunnel_exit)
            new_state = DeliveryState(tunnel_exit, self.goal_pos,
                                     state.cost_so_far + tunnel_cost)
            successors.append((new_state, "tunnel", tunnel_cost))
        
        return successors
    
    def get_cost_of_actions(self, actions):
        """Calculate total cost for a sequence of actions by simulating"""
        # Simulate actions from start
        current_pos = self.start_pos
        total_cost = 0
        
        for action in actions:
            if action == "up":
                new_pos = Position(current_pos.x, current_pos.y - 1)
            elif action == "down":
                new_pos = Position(current_pos.x, current_pos.y + 1)
            elif action == "left":
                new_pos = Position(current_pos.x - 1, current_pos.y)
            elif action == "right":
                new_pos = Position(current_pos.x + 1, current_pos.y)
            elif action == "tunnel":
                new_pos = self.grid.get_tunnel_exit(current_pos)
                if new_pos is None:
                    return float('inf')  # Invalid tunnel action
                total_cost += current_pos.manhattan_distance(new_pos)
                current_pos = new_pos
                continue
            else:
                return float('inf')  # Invalid action
            
            # Check if move is valid
            if self.grid.is_blocked(current_pos, new_pos):
                return float('inf')
            
            # Add traffic cost
            traffic = self.grid.get_traffic_level(current_pos, new_pos)
            if traffic is None:
                return float('inf')
            
            total_cost += traffic
            current_pos = new_pos
        
        return total_cost