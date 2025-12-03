# Search/generic_search.py
from collections import deque
import heapq
from .Tree_node import Node
from .Heuristics import HEURISTICS

class GenericSearch:
    """Generic search implementation with different strategies"""
    
    def __init__(self, problem, strategy="BF", heuristic_name='manhattan'):
        self.problem = problem
        self.strategy = strategy
        self.heuristic_name = heuristic_name
        self.nodes_expanded = 0
        self.max_memory = 0
    
    def solve(self):
        """Main solve method - returns (plan, cost, nodes_expanded)"""
        start_state = self.problem.get_start_state()
        start_node = Node(state=start_state, path_cost=0, depth=0)
        
        # Set heuristic for start node
        if self.strategy.startswith("GR") or self.strategy.startswith("AS"):
            start_node.heuristic = self._calculate_heuristic(start_state)
        
        if self.strategy == "BF":
            return self.breadth_first_search(start_node)
        elif self.strategy == "DF":
            return self.depth_first_search(start_node)
        elif self.strategy == "ID":
            return self.iterative_deepening_search(start_node)
        elif self.strategy == "UC":
            return self.uniform_cost_search(start_node)
        elif self.strategy.startswith("GR"):
            heuristic_num = int(self.strategy[2]) if len(self.strategy) > 2 else 1
            return self.greedy_search(start_node, heuristic_num)
        elif self.strategy.startswith("AS"):
            heuristic_num = int(self.strategy[2]) if len(self.strategy) > 2 else 1
            return self.a_star_search(start_node, heuristic_num)
        else:
            raise ValueError(f"Unknown search strategy: {self.strategy}")
    
    def _calculate_heuristic(self, state):
        """Calculate heuristic value for a state"""
        # Get goal position from problem
        goal_pos = self.problem.goal_pos
        
        # Select heuristic based on heuristic_name
        if self.heuristic_name == 'manhattan':
            return state.current_pos.manhattan_distance(goal_pos)
        elif self.heuristic_name == 'zero':
            return 0
        elif self.heuristic_name == 'diagonal':
            dx = abs(state.current_pos.x - goal_pos.x)
            dy = abs(state.current_pos.y - goal_pos.y)
            return max(dx, dy)
        elif self.heuristic_name == 'euclidean':
            dx = state.current_pos.x - goal_pos.x
            dy = state.current_pos.y - goal_pos.y
            return (dx**2 + dy**2)**0.5
        else:
            return state.current_pos.manhattan_distance(goal_pos)  # default
    
    def breadth_first_search(self, start_node):
        """BFS implementation"""
        if self.problem.is_goal_state(start_node.state):
            return [], 0, 0
        
        frontier = deque([start_node])
        explored = set()
        
        while frontier:
            # Update max memory usage
            self.max_memory = max(self.max_memory, len(frontier) + len(explored))
            
            node = frontier.popleft()
            self.nodes_expanded += 1
            
            if node.state in explored:
                continue
            explored.add(node.state)
            
            for state, action, cost in self.problem.get_successors(node.state):
                if state in explored:
                    continue
                
                child = Node(state=state, 
                           parent=node, 
                           action=action,
                           path_cost=node.path_cost + cost,
                           depth=node.depth + 1)
                
                if self.problem.is_goal_state(state):
                    return child.get_path(), child.path_cost, self.nodes_expanded
                
                frontier.append(child)
        
        return None, float('inf'), self.nodes_expanded  # No solution
    
    def depth_first_search(self, start_node, limit=float('inf')):
        """DFS implementation with optional depth limit"""
        frontier = [start_node]  # Stack
        explored = set()
        
        while frontier:
            self.max_memory = max(self.max_memory, len(frontier) + len(explored))
            
            node = frontier.pop()  # LIFO
            self.nodes_expanded += 1
            
            if self.problem.is_goal_state(node.state):
                return node.get_path(), node.path_cost, self.nodes_expanded
            
            if node.state in explored or node.depth >= limit:
                continue
            explored.add(node.state)
            
            # Add successors to frontier (in reverse order for consistent exploration)
            successors = self.problem.get_successors(node.state)
            successors.reverse()  # To explore in consistent order
            
            for state, action, cost in successors:
                if state in explored:
                    continue
                
                child = Node(state=state,
                           parent=node,
                           action=action,
                           path_cost=node.path_cost + cost,
                           depth=node.depth + 1)
                frontier.append(child)
        
        return None, float('inf'), self.nodes_expanded
    
    def iterative_deepening_search(self, start_node):
        """Iterative deepening search"""
        depth = 0
        total_nodes_expanded = 0
        
        while True:
            self.nodes_expanded = 0
            self.max_memory = 0
            result = self.depth_first_search(start_node, limit=depth)
            
            total_nodes_expanded += self.nodes_expanded
            
            path, cost, _ = result
            if path is not None:
                return path, cost, total_nodes_expanded
            
            depth += 1
            
            # Optional: depth limit to prevent infinite loop
            if depth > 1000:
                return None, float('inf'), total_nodes_expanded
    
    def uniform_cost_search(self, start_node):
        """UCS implementation (Dijkstra's algorithm)"""
        if self.problem.is_goal_state(start_node.state):
            return [], 0, 0
        
        frontier = []
        heapq.heappush(frontier, (start_node.path_cost, start_node))
        explored = set()
        cost_so_far = {start_node.state: 0}
        
        while frontier:
            self.max_memory = max(self.max_memory, len(frontier) + len(explored))
            
            _, node = heapq.heappop(frontier)
            self.nodes_expanded += 1
            
            if self.problem.is_goal_state(node.state):
                return node.get_path(), node.path_cost, self.nodes_expanded
            
            if node.state in explored:
                continue
            explored.add(node.state)
            
            for state, action, cost in self.problem.get_successors(node.state):
                new_cost = node.path_cost + cost
                
                if state not in cost_so_far or new_cost < cost_so_far[state]:
                    cost_so_far[state] = new_cost
                    
                    child = Node(state=state,
                               parent=node,
                               action=action,
                               path_cost=new_cost,
                               depth=node.depth + 1)
                    
                    heapq.heappush(frontier, (new_cost, child))
        
        return None, float('inf'), self.nodes_expanded
    
    def greedy_search(self, start_node, heuristic_num=1):
        """Greedy best-first search"""
        # Select heuristic
        if heuristic_num == 1:
            heuristic_func = lambda s: s.current_pos.manhattan_distance(self.problem.goal_pos)
        elif heuristic_num == 2:
            # Alternative heuristic: diagonal distance
            heuristic_func = lambda s: max(
                abs(s.current_pos.x - self.problem.goal_pos.x),
                abs(s.current_pos.y - self.problem.goal_pos.y)
            )
        else:
            heuristic_func = lambda s: 0
        
        if self.problem.is_goal_state(start_node.state):
            return [], 0, 0
        
        frontier = []
        start_heuristic = heuristic_func(start_node.state)
        heapq.heappush(frontier, (start_heuristic, start_node))
        explored = set()
        
        while frontier:
            self.max_memory = max(self.max_memory, len(frontier) + len(explored))
            
            _, node = heapq.heappop(frontier)
            self.nodes_expanded += 1
            
            if self.problem.is_goal_state(node.state):
                return node.get_path(), node.path_cost, self.nodes_expanded
            
            if node.state in explored:
                continue
            explored.add(node.state)
            
            for state, action, cost in self.problem.get_successors(node.state):
                if state in explored:
                    continue
                
                child = Node(state=state,
                           parent=node,
                           action=action,
                           path_cost=node.path_cost + cost,
                           depth=node.depth + 1,
                           heuristic=heuristic_func(state))
                
                heapq.heappush(frontier, (child.heuristic, child))
        
        return None, float('inf'), self.nodes_expanded
    
    def a_star_search(self, start_node, heuristic_num=1):
        """A* search algorithm"""
        # Select heuristic
        if heuristic_num == 1:
            heuristic_func = lambda s: s.current_pos.manhattan_distance(self.problem.goal_pos)
        elif heuristic_num == 2:
            # Alternative heuristic: diagonal distance (admissible for 4-direction movement)
            heuristic_func = lambda s: max(
                abs(s.current_pos.x - self.problem.goal_pos.x),
                abs(s.current_pos.y - self.problem.goal_pos.y)
            )
        else:
            heuristic_func = lambda s: 0
        
        if self.problem.is_goal_state(start_node.state):
            return [], 0, 0
        
        frontier = []
        start_f = start_node.path_cost + heuristic_func(start_node.state)
        heapq.heappush(frontier, (start_f, start_node))
        explored = set()
        cost_so_far = {start_node.state: start_node.path_cost}
        
        while frontier:
            self.max_memory = max(self.max_memory, len(frontier) + len(explored))
            
            _, node = heapq.heappop(frontier)
            self.nodes_expanded += 1
            
            if self.problem.is_goal_state(node.state):
                return node.get_path(), node.path_cost, self.nodes_expanded
            
            if node.state in explored:
                continue
            explored.add(node.state)
            
            for state, action, cost in self.problem.get_successors(node.state):
                new_cost = node.path_cost + cost
                
                if state not in cost_so_far or new_cost < cost_so_far[state]:
                    cost_so_far[state] = new_cost
                    
                    heuristic = heuristic_func(state)
                    child = Node(state=state,
                               parent=node,
                               action=action,
                               path_cost=new_cost,
                               depth=node.depth + 1,
                               heuristic=heuristic)
                    
                    f_value = new_cost + heuristic
                    heapq.heappush(frontier, (f_value, child))
        
        return None, float('inf'), self.nodes_expanded