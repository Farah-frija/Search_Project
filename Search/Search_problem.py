# Search/search_problem.py
from abc import ABC, abstractmethod

class SearchProblem(ABC):
    """Abstract base class for search problems"""
    
    @abstractmethod
    def get_start_state(self):
        """Returns the start state for the search problem"""
        pass
    
    @abstractmethod
    def is_goal_state(self, state):
        """Returns True if state is a goal state"""
        pass
    
    @abstractmethod
    def get_successors(self, state):
        """
        Returns list of (successor_state, action, step_cost) tuples
        where:
          - successor_state: the new state after taking action
          - action: string describing the action ("up", "down", etc.)
          - step_cost: cost of taking this action
        """
        pass
    
    @abstractmethod
    def get_cost_of_actions(self, actions):
        """Returns total cost of a sequence of actions"""
        pass