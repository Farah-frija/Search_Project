# Tests/test_grid_generator.py
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from GridGenerator.gridGenerator import GridGenerator
from Parsers.InputParser import parse_input_with_stores

def analyze_traffic(grid):
    """Analyze and display traffic information from grid"""
    # Count obstacles and traffic costs
    obstacles = 0
    traffic_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    
    for traffic in grid.traffic.values():
        if traffic == 0:
            obstacles += 1
        elif traffic in traffic_counts:
            traffic_counts[traffic] += 1
    
    total_segments = len(grid.traffic)
    
    print(f"  Traffic Analysis:")
    print(f"    Total segments: {total_segments}")
    print(f"    Obstacles (0): {obstacles} ({obstacles/total_segments*100:.1f}%)")
    
    # Display traffic cost distribution
    print(f"    Traffic cost distribution:")
    for cost in sorted(traffic_counts.keys()):
        count = traffic_counts[cost]
        if count > 0:
            percentage = count/total_segments*100
            print(f"      Cost {cost}: {count} segments ({percentage:.1f}%)")
    
    return obstacles, traffic_counts

def test_grid_generator():
    print("=== Testing Grid Generator ===")
    generator = GridGenerator(seed=42)  # Fixed seed for reproducibility
    
    # Test 1: Basic generation with custom parameters
    print("\nTest 1: Basic grid generation with analysis")
    init_str, traffic_str, stores = generator.generate_grid(
        min_m=5, max_m=5,
        min_n=5, max_n=5,
        min_stores=2, max_stores=2,
        min_customers=3, max_customers=3,
        min_tunnels=1,
        min_obstacle_prob=0.05,
        max_obstacle_prob=0.15,
        min_traffic=1,
        max_traffic=4
    )
    
    print(f"initState: {init_str[:50]}...")  # Show first 50 chars
    print(f"Traffic string: {len(traffic_str)} chars")
    print(f"Number of stores: {len(stores)}")
    print(f"Store positions: {stores}")
    
    try:
        grid = parse_input_with_stores(init_str, traffic_str, stores)
        print(f"✓ Successfully parsed generated grid")
        print(f"  Grid: {grid.m}x{grid.n}")
        print(f"  Customers: {len(grid.customers)} at {grid.customers}")
        print(f"  Tunnels: {len(grid.tunnels)//2}")
        
        # Display tunnel details
        if grid.tunnels:
            print(f"  Tunnel details:")
            seen = set()
            for entrance, exit_pos in grid.tunnels.items():
                if (entrance, exit_pos) not in seen and (exit_pos, entrance) not in seen:
                    distance = entrance.manhattan_distance(exit_pos)
                    print(f"    {entrance} <-> {exit_pos} (cost: {distance})")
                    seen.add((entrance, exit_pos))
        
        # Analyze traffic
        obstacles, traffic_counts = analyze_traffic(grid)
        
    except Exception as e:
        print(f"✗ Error parsing generated grid: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: GenGrid() function with detailed analysis
    print("\n" + "="*60)
    print("Test 2: GenGrid() function with detailed analysis")
    print("="*60)
    
    grid, init_str, traffic_str = generator.gen_grid()
    
    print(f"Generated grid: {grid.m}x{grid.n}")
    print(f"Stores: {grid.stores}")
    print(f"Customers: {grid.customers}")
    
    # Count tunnels
    tunnel_pairs = set()
    for entrance, exit_pos in grid.tunnels.items():
        tunnel_pairs.add(tuple(sorted([(entrance.x, entrance.y), (exit_pos.x, exit_pos.y)])))
    
    print(f"Tunnels: {len(tunnel_pairs)}")
    for i, (pos1, pos2) in enumerate(tunnel_pairs):
        pos1_obj = type('', (), {'x': pos1[0], 'y': pos1[1]})()
        pos2_obj = type('', (), {'x': pos2[0], 'y': pos2[1]})()
        distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        print(f"  Tunnel {i+1}: {pos1} <-> {pos2} (Manhattan distance: {distance})")
    
    # Detailed traffic analysis
    obstacles, traffic_counts = analyze_traffic(grid)
    
    # Test 3: Multiple generations with statistics
    print("\n" + "="*60)
    print("Test 3: Multiple random generations with statistics")
    print("="*60)
    
    stats = {
        'total_obstacles': 0,
        'traffic_totals': {1: 0, 2: 0, 3: 0, 4: 0},
        'tunnel_counts': [],
        'grid_sizes': []
    }
    
    for i in range(5):
        print(f"\n--- Run {i+1} ---")
        generator2 = GridGenerator()  # No seed - truly random
        init_str, traffic_str, stores = generator2.generate_grid(
            min_tunnels=1,
            min_obstacle_prob=0.05,
            max_obstacle_prob=0.2
        )
        grid = parse_input_with_stores(init_str, traffic_str, stores)
        
        print(f"Grid: {grid.m}x{grid.n}")
        
        # Tunnels
        tunnel_pairs = set()
        for entrance, exit_pos in grid.tunnels.items():
            tunnel_pairs.add(tuple(sorted([(entrance.x, entrance.y), (exit_pos.x, exit_pos.y)])))
        
        stats['tunnel_counts'].append(len(tunnel_pairs))
        stats['grid_sizes'].append((grid.m, grid.n))
        print(f"Tunnels: {len(tunnel_pairs)}")
        
        # Traffic analysis
        obstacles, traffic_counts = analyze_traffic(grid)
        stats['total_obstacles'] += obstacles
        for cost, count in traffic_counts.items():
            stats['traffic_totals'][cost] += count
    
    # Print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS (5 runs)")
    print("="*60)
    
    if stats['grid_sizes']:
        avg_m = sum(m for m, n in stats['grid_sizes']) / len(stats['grid_sizes'])
        avg_n = sum(n for m, n in stats['grid_sizes']) / len(stats['grid_sizes'])
        print(f"Average grid size: {avg_m:.1f}x{avg_n:.1f}")
    
    if stats['tunnel_counts']:
        avg_tunnels = sum(stats['tunnel_counts']) / len(stats['tunnel_counts'])
        min_tunnels = min(stats['tunnel_counts'])
        max_tunnels = max(stats['tunnel_counts'])
        print(f"Tunnels per grid: min={min_tunnels}, avg={avg_tunnels:.1f}, max={max_tunnels}")
    
    total_segments_all = stats['total_obstacles'] + sum(stats['traffic_totals'].values())
    if total_segments_all > 0:
        print(f"\nTraffic cost distribution across all runs:")
        print(f"  Obstacles: {stats['total_obstacles']} ({stats['total_obstacles']/total_segments_all*100:.1f}%)")
        
        for cost in sorted(stats['traffic_totals'].keys()):
            count = stats['traffic_totals'][cost]
            if count > 0:
                percentage = count/total_segments_all*100
                print(f"  Cost {cost}: {count} ({percentage:.1f}%)")
    
    # Test 4: Verify minimum requirements
    print("\n" + "="*60)
    print("Test 4: Verify minimum requirements")
    print("="*60)

    test_cases = [
        ("Small", 4, 4, 1, 1),
        ("Medium", 6, 6, 2, 3),
    ]

    all_passed = True
    for name, m, n, s, c in test_cases:
        print(f"\n{name} grid ({m}x{n}, {s} stores, {c} customers):")

        try:
            # Get grid strings
            init_str, traffic_str, stores = generator.generate_grid(
                min_m=m, max_m=m,
                min_n=n, max_n=n,
                min_stores=s, max_stores=s,
                min_customers=c, max_customers=c,
                min_tunnels=1
            )

            # Parse to Grid object
            grid = parse_input_with_stores(init_str, traffic_str, stores)

            # Check tunnels
            tunnel_pairs = set()
            for entrance, exit_pos in grid.tunnels.items():
                tunnel_pairs.add(tuple(sorted([(entrance.x, entrance.y), (exit_pos.x, exit_pos.y)])))

            tunnel_count = len(tunnel_pairs)
            has_tunnel = tunnel_count >= 1
            print(f"  Tunnels: {tunnel_count} {'✓' if has_tunnel else '✗'}")

            # Check obstacles
            obstacles = sum(1 for t in grid.traffic.values() if t == 0)
            has_obstacles = obstacles > 0
            print(f"  Obstacles: {obstacles} {'✓' if has_obstacles else '✗'}")

            # Check all segments have traffic data
            expected_segments = (n * (m-1)) + (m * (n-1))
            actual_segments = len(grid.traffic)
            all_segments = expected_segments == actual_segments
            print(f"  All segments generated: {actual_segments}/{expected_segments} {'✓' if all_segments else '✗'}")

            if not (has_tunnel and has_obstacles and all_segments):
                all_passed = False

        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_passed = False

    if all_passed:
        print("\n✓ All minimum requirements met!")
    else:
        print("\n✗ Some requirements not met!")
test_grid_generator()