# Delivery/delivery_search.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Search.Delivery_problem import DeliveryProblem
from Search.Generic_search import GenericSearch
from DataStructure.Position import Position
from GridGenerator.gridGenerator import GridGenerator
    
class DeliverySearch:
    """Search implementation for package delivery"""
    
    @staticmethod
    def path(grid, start_pos, goal_pos, strategy="BF"):
        """
        Find path from start to goal.
        Returns: "plan;cost;nodesExpanded"
        """
        # Create problem
        problem = DeliveryProblem(grid, start_pos, goal_pos)
        
        # Run search
        search = GenericSearch(problem, strategy=strategy)
        actions, cost, nodes_expanded = search.solve()
        
        if actions is None:
            return "NO_PATH;inf;{}".format(nodes_expanded)
        
        # Format output
        plan_str = ",".join(actions)
        return "{};{};{}".format(plan_str, cost, nodes_expanded)
    
    @staticmethod
    def GenGrid():
        """
        Randomly generates a complete grid.
        Returns: (grid_object, init_str, traffic_str)
        """
   
        
        generator = GridGenerator()
        # This returns everything as in your tests
        return generator.gen_grid()