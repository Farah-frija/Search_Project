# Analysis/algorithm_analyzer.py
import time
import tracemalloc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Delivery.Delivery_Search import DeliverySearch

class AlgorithmAnalyzer:
    """
    Comprehensive analysis of all search algorithms.
    Computes: cost, nodes expanded, time, memory for each algorithm.
    """
    
    def __init__(self, grid):
        self.grid = grid
        self.metrics = {}
        
        # All algorithms to test
        self.algorithms = {
            "BF": "Breadth-First Search",
            "DF": "Depth-First Search", 
            "ID": "Iterative Deepening",
            "UC": "Uniform Cost Search",
            "GR1": "Greedy Search (Heuristic 1)",
            "GR2": "Greedy Search (Heuristic 2)",
            "AS1": "A* Search (Heuristic 1)",
            "AS2": "A* Search (Heuristic 2)"
        }
    
    def analyze_single_path(self, start_pos, goal_pos):
        """
        Analyze ALL algorithms for a single path.
        Returns metrics dictionary for all algorithms.
        """
        print(f"\nAnalyzing path: {start_pos} → {goal_pos}")
        print("-" * 50)
        
        path_metrics = {}
        
        for algo_code, algo_name in self.algorithms.items():
            print(f"  {algo_code:<4} ({algo_name[:20]:<20})...", end="", flush=True)
            
            try:
                # Start memory tracking
                tracemalloc.start()
                
                # Start timing
                start_time = time.time()
                
                # Run the search
                result = DeliverySearch.path(self.grid, start_pos, goal_pos, algo_code)
                plan_str, cost_str, nodes_str = result.split(';')
                
                # Stop timing
                elapsed = time.time() - start_time
                
                # Get memory usage
                current, peak = tracemalloc.get_trafficced_memory()
                tracemalloc.stop()
                
                # Parse results
                cost = float(cost_str) if cost_str != 'inf' else float('inf')
                nodes = int(nodes_str)
                
                # Store metrics
                path_metrics[algo_code] = {
                    'algorithm': algo_name,
                    'cost': cost,
                    'nodes_expanded': nodes,
                    'time_ms': elapsed * 1000,  # Convert to milliseconds
                    'memory_peak_kb': peak / 1024,  # Convert to KB
                    'memory_current_kb': current / 1024,
                    'path_found': plan_str != "NO_PATH",
                    'path_length': len(plan_str.split(',')) if plan_str != "NO_PATH" else 0,
                    'path_sample': plan_str[:30] + "..." if len(plan_str) > 30 else plan_str
                }
                
                print(f" ✓ Cost: {cost}, Nodes: {nodes}, Time: {elapsed:.3f}s")
                
            except Exception as e:
                print(f" ✗ Error: {e}")
                path_metrics[algo_code] = {
                    'algorithm': algo_name,
                    'error': str(e),
                    'cost': float('inf'),
                    'nodes_expanded': 0,
                    'time_ms': 0,
                    'memory_peak_kb': 0,
                    'path_found': False
                }
        
        return path_metrics
    
    def analyze_grid_scenarios(self, num_scenarios=3):
        """
        Analyze multiple path scenarios in the grid.
        Returns comprehensive metrics for all algorithms.
        """
        print("\n" + "="*70)
        print("COMPREHENSIVE ALGORITHM ANALYSIS")
        print("="*70)
        
        # Grid info
        print(f"\nGrid: {self.grid.m}x{self.grid.n}")
        print(f"Stores: {len(self.grid.stores)} - {self.grid.stores}")
        print(f"Customers: {len(self.grid.customers)} - {self.grid.customers}")
        
        all_metrics = {
            'grid_info': {
                'dimensions': (self.grid.m, self.grid.n),
                'store_count': len(self.grid.stores),
                'customer_count': len(self.grid.customers),
                'traffic_segments': len(self.grid.traffic),
                'obstacles': sum(1 for t in self.grid.traffic.values() if t == 0),
                'tunnels': len(self.grid.tunnels) // 2
            },
            'scenarios': {},
            'summary': {}
        }
        
        # Analyze multiple store-customer pairs
        scenario_num = 0
        max_scenarios = min(num_scenarios, 
                           len(self.grid.stores) * len(self.grid.customers))
        
        for store_idx, store in enumerate(self.grid.stores):
            for customer_idx, customer in enumerate(self.grid.customers):
                if scenario_num >= max_scenarios:
                    break
                
                scenario_key = f"S{store_idx}_C{customer_idx}"
                print(f"\n[Scenario {scenario_num+1}/{max_scenarios}] {scenario_key}")
                print(f"  Store: {store}, Customer: {customer}")
                print(f"  Manhattan distance: {store.manhattan_distance(customer)}")
                
                # Analyze this path with all algorithms
                scenario_metrics = self.analyze_single_path(store, customer)
                all_metrics['scenarios'][scenario_key] = scenario_metrics
                
                scenario_num += 1
        
        # Generate summary statistics
        all_metrics['summary'] = self._generate_summary(all_metrics['scenarios'])
        
        return all_metrics
    
    def _generate_summary(self, scenarios_metrics):
        """
        Generate summary statistics across all scenarios.
        """
        summary = {
            'by_algorithm': {},
            'optimality_analysis': {},
            'efficiency_ranking': {}
        }
        
        # Initialize data structure
        for algo_code in self.algorithms.keys():
            summary['by_algorithm'][algo_code] = {
                'total_cost': 0,
                'total_nodes': 0,
                'total_time': 0,
                'max_memory': 0,
                'success_count': 0,
                'scenario_count': 0
            }
        
        # Aggregate across scenarios
        for scenario_key, algo_metrics in scenarios_metrics.items():
            for algo_code, metrics in algo_metrics.items():
                if algo_code in summary['by_algorithm']:
                    algo_summary = summary['by_algorithm'][algo_code]
                    algo_summary['scenario_count'] += 1
                    
                    if metrics.get('path_found', False):
                        algo_summary['success_count'] += 1
                        algo_summary['total_cost'] += metrics['cost']
                        algo_summary['total_nodes'] += metrics['nodes_expanded']
                        algo_summary['total_time'] += metrics['time_ms']
                        algo_summary['max_memory'] = max(
                            algo_summary['max_memory'], 
                            metrics['memory_peak_kb']
                        )
        
        # Calculate averages
        for algo_code, data in summary['by_algorithm'].items():
            if data['success_count'] > 0:
                data['avg_cost'] = data['total_cost'] / data['success_count']
                data['avg_nodes'] = data['total_nodes'] / data['success_count']
                data['avg_time'] = data['total_time'] / data['success_count']
            else:
                data['avg_cost'] = float('inf')
                data['avg_nodes'] = 0
                data['avg_time'] = 0
        
        # Find optimal algorithms (lowest cost)
        optimal_cost = float('inf')
        optimal_algorithms = []
        
        for algo_code, data in summary['by_algorithm'].items():
            if data['avg_cost'] < optimal_cost:
                optimal_cost = data['avg_cost']
                optimal_algorithms = [algo_code]
            elif data['avg_cost'] == optimal_cost:
                optimal_algorithms.append(algo_code)
        
        summary['optimality_analysis'] = {
            'optimal_cost': optimal_cost,
            'optimal_algorithms': optimal_algorithms,
            'is_consistent': len(optimal_algorithms) > 0
        }
        
        # Rank by efficiency (nodes/time)
        efficiency_scores = []
        for algo_code, data in summary['by_algorithm'].items():
            if data['success_count'] > 0:
                # Lower nodes and time = better efficiency
                efficiency_score = (data['avg_nodes'] * data['avg_time']) / 1000
                efficiency_scores.append((algo_code, efficiency_score))
        
        efficiency_scores.sort(key=lambda x: x[1])
        summary['efficiency_ranking'] = efficiency_scores
        
        return summary
    
    def print_detailed_report(self, analysis_results):
        """
        Print a detailed report of the analysis.
        """
        print("\n" + "="*70)
        print("DETAILED ALGORITHM ANALYSIS REPORT")
        print("="*70)
        
        # Grid info
        grid_info = analysis_results['grid_info']
        print(f"\nGRID INFORMATION:")
        print(f"  Dimensions: {grid_info['dimensions'][0]}x{grid_info['dimensions'][1]}")
        print(f"  Stores: {grid_info['store_count']}")
        print(f"  Customers: {grid_info['customer_count']}")
        print(f"  Traffic segments: {grid_info['traffic_segments']}")
        print(f"  Obstacles: {grid_info['obstacles']}")
        print(f"  Tunnels: {grid_info['tunnels']}")
        
        # Per scenario details
        print(f"\nPER-SCENARIO METRICS:")
        print("-" * 70)
        
        for scenario_key, algo_metrics in analysis_results['scenarios'].items():
            print(f"\n{scenario_key}:")
            print(f"{'Algo':<6} {'Cost':<8} {'Nodes':<10} {'Time(ms)':<12} {'Memory(KB)':<12} {'Path'}")
            print("-" * 70)
            
            for algo_code, metrics in algo_metrics.items():
                if metrics.get('path_found', False):
                    print(f"{algo_code:<6} {metrics['cost']:<8.1f} "
                          f"{metrics['nodes_expanded']:<10} "
                          f"{metrics['time_ms']:<12.2f} "
                          f"{metrics['memory_peak_kb']:<12.1f} "
                          f"{metrics['path_sample']}")
                else:
                    print(f"{algo_code:<6} {'NO_PATH':<8} {'-':<10} {'-':<12} {'-':<12} {'-'}")
        
        # Summary
        print(f"\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        
        summary = analysis_results['summary']
        print(f"\nPERFORMANCE BY ALGORITHM (averages):")
        print(f"{'Algo':<6} {'Avg Cost':<10} {'Avg Nodes':<12} {'Avg Time(ms)':<14} {'Max Memory(KB)':<15} {'Success Rate'}")
        print("-" * 80)
        
        for algo_code, data in summary['by_algorithm'].items():
            success_rate = (data['success_count'] / data['scenario_count'] * 100) if data['scenario_count'] > 0 else 0
            print(f"{algo_code:<6} {data.get('avg_cost', float('inf')):<10.1f} "
                  f"{data.get('avg_nodes', 0):<12.0f} "
                  f"{data.get('avg_time', 0):<14.2f} "
                  f"{data['max_memory']:<15.1f} "
                  f"{success_rate:.1f}%")
        
        # Optimality analysis
        opt = summary['optimality_analysis']
        print(f"\nOPTIMALITY ANALYSIS:")
        print(f"  Optimal cost: {opt['optimal_cost']:.1f}")
        print(f"  Algorithms achieving optimal cost: {', '.join(opt['optimal_algorithms'])}")
        
        # Efficiency ranking
        print(f"\nEFFICIENCY RANKING (lower is better):")
        for rank, (algo_code, score) in enumerate(summary['efficiency_ranking'], 1):
            print(f"  {rank}. {algo_code}: {score:.2f}")
        
        # Recommendations
        print(f"\nRECOMMENDATIONS:")
        if 'UC' in opt['optimal_algorithms'] or 'AS1' in opt['optimal_algorithms'] or 'AS2' in opt['optimal_algorithms']:
            print("  ✅ Use A* (AS1/AS2) or UCS for optimal solutions")
        
        fastest_optimal = min(opt['optimal_algorithms'], 
                             key=lambda a: summary['by_algorithm'][a]['avg_time'])
        print(f"  ⚡ Fastest optimal algorithm: {fastest_optimal}")
        
        most_efficient = summary['efficiency_ranking'][0][0] if summary['efficiency_ranking'] else "N/A"
        print(f"  📊 Most efficient overall: {most_efficient}")

# Test function using the class
def test_algorithm_analyzer():
    """Test the AlgorithmAnalyzer class"""
    print("Testing AlgorithmAnalyzer Class")
    print("="*70)
    
    # Generate a test grid
    from GridGenerator.gridGenerator import GridGenerator
    
    generator = GridGenerator(seed=42)
    grid, init_str, traffic_str = generator.gen_grid()
    
    print(f"Generated grid: {grid.m}x{grid.n}")
    print(f"Stores: {grid.stores}")
    print(f"Customers: {grid.customers}")
    
    # Create analyzer
    analyzer = AlgorithmAnalyzer(grid)
    
    # Analyze the grid
    results = analyzer.analyze_grid_scenarios(num_scenarios=2)
    
    # Print report
    analyzer.print_detailed_report(results)
    
    return results


test_algorithm_analyzer()