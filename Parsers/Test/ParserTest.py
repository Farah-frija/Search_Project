import sys
import os

# Get the current script's directory (Parsers/Test/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to Parsers/
parsers_dir = os.path.dirname(current_dir)
# Go up another level to IA_Project/
project_root = os.path.dirname(parsers_dir)

# Add both to Python path
sys.path.append(project_root)
sys.path.append(parsers_dir)
import InputParser as parser

import DataStructure.Position as position
import DataStructure.Edge as edge 

    


def test_basic_parsing():
    print("=== Test 1: Basic Parsing ===")
    
    # Example from PDF (adapted)
    init_str = "10;8;3;2;1,4,5,2,7,3;0,0,3,3,4,4,9,7"  
    # m=10, n=8, P=3, S=2, customers: (1,4),(5,2),(7,3), tunnels: (0,0)-(3,3) and (4,4)-(9,7)
    
    traffic_str = "0,0,0,1,2;0,1,0,2,3;1,0,1,1,4;1,1,1,2,1;5,2,5,3,0"  # last one blocked
    
    try:
        grid = parser.parse_input(init_str, traffic_str)
        
        print(f"Grid dimensions: {grid.m}x{grid.n}")
        print(f"Customers: {grid.customers}")
        print(f"Number of tunnels: {len(grid.tunnels)//2}")  # bidirectional counted twice
        print(f"Number of traffic segments: {len(grid.traffic)}")
        
        # Check a specific traffic segment
        test_edge = edge.Edge(position.Position(0,0), position.Position(0,1))
        print(f"Traffic from (0,0) to (0,1): {grid.get_traffic_level(position.Position(0,0), position.Position(0,1))}")
        print(f"Is (0,0)-(0,1) blocked? {grid.is_blocked(position.Position(0,0), position.Position(0,1))}")
        
        # Check blocked segment
        print(f"Is (5,2)-(5,3) blocked? {grid.is_blocked(position.Position(5,2), position.Position(5,3))}")
        
        # Check tunnel
        print(f"Tunnel from (0,0) exits to: {grid.get_tunnel_exit(position.Position(0,0))}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_missing_traffic():
    print("\n=== Test 2: Missing Traffic Segment ===")
    
    init_str = "5;5;1;1;2,2;;"  # Simple grid, no tunnels
    traffic_str = "0,0,0,1,2;0,1,0,2,1"  # Only some segments defined
    
    grid =parser.parse_input(init_str, traffic_str)
    
    # Defined segment
    print(f"Defined segment (0,0)-(0,1): traffic={grid.get_traffic_level(position.Position(0,0), position.Position(0,1))}")
    
    # Undefined segment - what happens?
    undefined_traffic = grid.get_traffic_level(position.Position(2,2), position.Position(2,3))
    print(f"Undefined segment (2,2)-(2,3): traffic={undefined_traffic}")
    print(f"Is it blocked? {grid.is_blocked(position.Position(2,2), position.Position(2,3))}")

def test_edge_equality():
    print("\n=== Test 3: Edge Equality (Bidirectional) ===")
    
    p1 = position.Position(0,0)
    p2 = position.Position(0,1)
    p3 = position.Position(1,0)
    
    edge1 = edge.Edge(p1, p2)
    edge2 = edge.Edge(p2, p1)  # Reverse should be equal
    edge3 = edge.Edge(p1, p3)  # Different
    
    print(f"Edge({p1},{p2}) == Edge({p2},{p1}): {edge1 == edge2}")
    print(f"Edge({p1},{p2}) == Edge({p1},{p3}): {edge1 == edge3}")
    
    # Test in dictionary
    traffic_dict = {}
    traffic_dict[edge1] = 2
    print(f"Dictionary with edge1 has key edge2: {edge2 in traffic_dict}")
    print(f"Value via edge2: {traffic_dict.get(edge2, 'not found')}")

def test_invalid_input():
    print("\n=== Test 4: Invalid Input Handling ===")
    
    # Missing parts
    bad_init = "5;5;1"  # Missing customer coords
    traffic = ""
    
    try:
        grid = parser.parse_input(bad_init, traffic)
        print("Should have raised error!")
    except ValueError as e:
        print(f"Correctly caught error: {e}")
    
    # Bad traffic format
    init_str = "5;5;1;1;2,2;;"
    bad_traffic = "0,0,0,1,2,3"  # Wrong number of values
    
    try:
        grid = parser.parse_input(init_str, bad_traffic)
        print("Should have raised error for bad traffic!")
    except Exception as e:
        print(f"Caught: {e}")

def test_tunnel_parsing():
    print("\n=== Test 5: Tunnel Parsing ===")
    
    # The PDF format seems odd: "TunnelX_1,TunnelY_1,TunnelX_1,TunnelY_1"
    # I think it's a typo and should be pairs: x1,y1,x2,y2 for each tunnel
    
    init_str = "10;10;2;1;3,3,7,7;0,0,9,9,2,2,8,8"  # Two tunnels
    
    grid = parser.parse_input(init_str, "")
    
    print(f"Tunnel entries in dict: {len(grid.tunnels)}")
    
    # Check first tunnel
    entrance1 = position.Position(0,0)
    exit1 = grid.get_tunnel_exit(entrance1)
    print(f"Tunnel from {entrance1} -> {exit1}")
    
    # Should be bidirectional
    back = grid.get_tunnel_exit(exit1)
    print(f"Reverse from {exit1} -> {back}")

if __name__ == "__main__":
    test_basic_parsing()
    test_missing_traffic()
    test_edge_equality()
    test_invalid_input()
    test_tunnel_parsing()