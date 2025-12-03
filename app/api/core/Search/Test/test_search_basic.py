# Tests/test_search_basic.py
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from DataStructure.Position import Position
from Search.Delivery_problem import DeliveryProblem
from Search.Generic_search import GenericSearch
from GridGenerator.gridGenerator import GridGenerator
from DataStructure.Grid import Grid
def create_test_grid_with_generator():
    """Create a test grid using GridGenerator"""
    print("Generating test grid with GridGenerator...")
    
    generator = GridGenerator(seed=123)  # Fixed seed for reproducibility
    
    # Generate a simple grid
    init_str, traffic_str, stores = generator.generate_grid(
        min_m=5, max_m=5,
        min_n=5, max_n=5,
        min_stores=1, max_stores=5,
        min_customers=1, max_customers=10,
        min_tunnels=0,  # No tunnels for simple test
        min_obstacle_prob=0.0,  # No obstacles for simple test
        max_obstacle_prob=0.0,
        min_traffic=1,
        max_traffic=4  # All traffic cost 1
    )
    
    print(f"Generated grid strings")
    print(f"  init_str: {init_str[:50]}...")
    print(f"  traffic_str length: {len(traffic_str)}")
    print(f"  stores: {stores}")
    
    # Parse the grid
    from Parsers.InputParser import parse_input_with_stores
    grid = parse_input_with_stores(init_str, traffic_str, stores)
    
    return grid

def test_basic_search_on_generated_grid():
    print("="*60)
    print("Testing Search on Generated Grid")
    print("="*60)
    
    # Generate grid
    grid = create_test_grid_with_generator()
    
    if grid is None:
        print("✗ Failed to generate grid")
        return
    
    print(f"\nGenerated Grid Details:")
    print(f"  Size: {grid.m}x{grid.n}")
    print(f"  Stores: {grid.stores}")
    print(f"  Customers: {grid.customers}")
    
    # Use first store and first customer
    if not grid.stores or not grid.customers:
        print("✗ No stores or customers in grid")
        return
    
    store = grid.stores[0]
    customer = grid.customers[0]
    
    print(f"\nDelivery Problem:")
    print(f"  From store: {store}")
    print(f"  To customer: {customer}")
    print(f"  Manhattan distance: {store.manhattan_distance(customer)}")
    
    # Create problem
    problem = DeliveryProblem(grid, store, customer)
    
    # Test different search strategies
    strategies = ["BF", "DF", "UC", "GR1", "AS1"]
    
    results = {}
    for strategy in strategies:
        print(f"\n--- Testing {strategy} ---")
        
        search = GenericSearch(problem, strategy=strategy)
        path, cost, nodes = search.solve()
        
        if path:
            print(f"  ✓ Path found: {len(path)} steps")
            print(f"     Cost: {cost}")
            print(f"     Nodes expanded: {nodes}")
            
            # Show first few steps
            if len(path) <= 10:
                print(f"     Path: {' -> '.join(path)}")
            else:
                print(f"     Path (first 5): {' -> '.join(path[:5])}...")
            
            # Verify path cost
            try:
                verified_cost = problem.get_cost_of_actions(path)
                if abs(verified_cost - cost) < 0.001:
                    print(f"     ✓ Cost verified")
                else:
                    print(f"     ✗ Cost mismatch: {cost} vs {verified_cost}")
            except Exception as e:
                print(f"     (Cost verification error: {e})")
        else:
            print(f"  ✗ No path found")
            print(f"     Nodes expanded: {nodes}")
        
        results[strategy] = (path, cost, nodes)
    
    # Compare results
    print("\n" + "="*60)
    print("Search Algorithm Comparison")
    print("="*60)
    
    print(f"{'Strategy':<8} {'Found':<8} {'Path Len':<10} {'Cost':<10} {'Nodes':<12}")
    print("-" * 50)
    
    for strategy in strategies:
        path, cost, nodes = results[strategy]
        if path:
            found = "YES"
            path_len = len(path)
        else:
            found = "NO"
            path_len = "N/A"
        
        print(f"{strategy:<8} {found:<8} {str(path_len):<10} {str(cost):<10} {nodes:<12}")
    
    # Verify optimality
    print("\n" + "-" * 60)
    print("Optimality Check:")
    
    # UCS should find optimal cost
    uc_path, uc_cost, _ = results.get("UC", (None, None, None))
    if uc_path:
        print(f"UCS (optimal) cost: {uc_cost}")
        
        # Check if A* matches UCS (should be optimal)
        as_path, as_cost, _ = results.get("AS1", (None, None, None))
        if as_path and abs(as_cost - uc_cost) < 0.001:
            print(f"✓ A* found optimal cost: {as_cost}")
        elif as_path:
            print(f"✗ A* cost differs: {as_cost} (should be {uc_cost})")
    else:
        print("UCS found no path")

def test_search_with_tunnel():
    """Test search when tunnel is available"""
    print("\n" + "="*60)
    print("Testing Search with Tunnel")
    print("="*60)
    
    generator = GridGenerator(seed=456)
    
    # Generate grid with a tunnel
    # We'll manually adjust to ensure a useful tunnel
    init_str = "5;5;1;1;4,4;0,0,4,4"  # Tunnel from (0,0) to (4,4)
    
    # Generate traffic (all cost 2 to make tunnel attractive)
    traffic_parts = []
    for y in range(5):
        for x in range(4):
            traffic_parts.append(f"{x},{y},{x+1},{y},2")
    
    for x in range(5):
        for y in range(4):
            traffic_parts.append(f"{x},{y},{x},{y+1},2")
    
    traffic_str = ";".join(traffic_parts)
    
    # Store at (0,0), customer at (4,4)
    stores = [Position(0, 0)]
    
    from Parsers.InputParser import parse_input_with_stores
    grid = parse_input_with_stores(init_str, traffic_str, stores)
    
    print(f"Grid with tunnel:")
    print(f"  Size: {grid.m}x{grid.n}")
    print(f"  Store: {grid.stores[0]}")
    print(f"  Customer: {grid.customers[0]}")
    
    tunnel_exit = grid.get_tunnel_exit(Position(0, 0))
    if tunnel_exit:
        tunnel_cost = Position(0, 0).manhattan_distance(tunnel_exit)
        print(f"  Tunnel: (0,0) -> {tunnel_exit} (cost: {tunnel_cost})")
    
    normal_path_cost = 8 * 2  # 8 steps * cost 2 = 16
    print(f"  Normal path cost (approx): {normal_path_cost}")
    
    # Create problem
    problem = DeliveryProblem(grid, grid.stores[0], grid.customers[0])
    
    # Test A* search
    print(f"\n--- Testing A* Search ---")
    search = GenericSearch(problem, strategy="AS1")
    path, cost, nodes = search.solve()
    
    if path:
        print(f"  ✓ Path found")
        print(f"     Cost: {cost}")
        print(f"     Nodes expanded: {nodes}")
        
        # Check if tunnel was used
        if "tunnel" in path:
            print(f"     ✓ Tunnel was used!")
            if cost == 8:  # Tunnel cost should be 8 (Manhattan distance)
                print(f"     ✓ Correct tunnel cost: {cost}")
            else:
                print(f"     ✗ Unexpected cost: {cost} (expected 8)")
        else:
            print(f"     ✗ Tunnel was NOT used")
            print(f"     Path: {' -> '.join(path[:3])}...")
    else:
        print(f"  ✗ No path found")

def test_unreachable_customer():
    """Test search when customer is unreachable"""
    print("\n" + "="*60)
    print("Testing Unreachable Customer")
    print("="*60)
    
    # Manually create a grid with obstacles blocking the path

    
    grid = Grid(4, 4)
    grid.add_store(Position(0, 0))
    grid.add_customer(Position(3, 3))
    
    # Add traffic - all normal except blocked middle
    for y in range(4):
        for x in range(3):
            grid.set_traffic(Position(x, y), Position(x+1, y), 1)
    
    for x in range(4):
        for y in range(3):
            grid.set_traffic(Position(x, y), Position(x, y+1), 1)
    
    # Block the critical path
    grid.set_traffic(Position(1, 1), Position(2, 1), 0)  # Blocked
    grid.set_traffic(Position(1, 1), Position(1, 2), 0)  # Blocked
    grid.set_traffic(Position(2, 1), Position(2, 2), 0)  # Blocked
    
    print(f"Grid with blocked middle:")
    print(f"  Size: {grid.m}x{grid.n}")
    print(f"  Store: {grid.stores[0]}")
    print(f"  Customer: {grid.customers[0]}")
    
    # Create problem
    problem = DeliveryProblem(grid, grid.stores[0], grid.customers[0])
    
    # Test BFS (should handle unreachable)
    print(f"\n--- Testing BFS on unreachable customer ---")
    search = GenericSearch(problem, strategy="BF")
    path, cost, nodes = search.solve()
    
    if path is None:
        print(f"  ✓ Correctly detected unreachable customer")
        print(f"     Nodes expanded: {nodes}")
    else:
        print(f"  ✗ Found path (should be unreachable)")
        print(f"     Path: {' -> '.join(path)}")

def run_all_tests():
    """Run all search tests"""
    print("Starting Search Algorithm Tests...")
    print("="*60)
    
    # Test 1: Basic search on generated grid
    test_basic_search_on_generated_grid()
    
    # Test 2: Search with tunnel
    test_search_with_tunnel()
    
    # Test 3: Unreachable customer
    test_unreachable_customer()
    
    print("\n" + "="*60)
    print("All Search Tests Completed!")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()