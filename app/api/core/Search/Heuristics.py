# Search/heuristics.py
from DataStructure.Position import Position

def manhattan_heuristic(state, goal_pos):
    """Heuristic 1: Manhattan distance to goal"""
    return state.current_pos.manhattan_distance(goal_pos)

def euclidean_heuristic(state, goal_pos):
    """Heuristic 2: Euclidean distance to goal (not admissible for Manhattan movement)"""
    dx = state.current_pos.x - goal_pos.x
    dy = state.current_pos.y - goal_pos.y
    return (dx**2 + dy**2)**0.5

def zero_heuristic(state, goal_pos):
    """Heuristic 3: Always returns 0 (admissible but not informative)"""
    return 0

def diagonal_heuristic(state, goal_pos):
    """Heuristic 4: Chebyshev distance (admissible for 4-direction movement)"""
    dx = abs(state.current_pos.x - goal_pos.x)
    dy = abs(state.current_pos.y - goal_pos.y)
    return max(dx, dy)

def double_manhattan_heuristic(state, goal_pos):
    """Heuristic 5: 2 * Manhattan distance (NOT admissible - for testing)"""
    return 2 * state.current_pos.manhattan_distance(goal_pos)

# Dictionary of available heuristics
HEURISTICS = {
    'manhattan': manhattan_heuristic,
    'euclidean': euclidean_heuristic,
    'zero': zero_heuristic,
    'diagonal': diagonal_heuristic,
    'double_manhattan': double_manhattan_heuristic  # Not admissible!
}