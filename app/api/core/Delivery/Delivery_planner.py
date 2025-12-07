# Delivery/delivery_planner.py
import sys
import os
import time
import tracemalloc
from typing import Dict, List, Tuple, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataStructure.Position import Position
from Search.Delivery_problem import DeliveryProblem
from Search.Generic_search import GenericSearch
from DataStructure.Grid import Grid

class DeliveryPlanner:
    """Plans which trucks deliver which packages"""
    
    def __init__(self, grid=None):
        self.grid = grid
        self.strategies = ["BF", "DF", "ID", "UC", "GR1", "GR2", "AS1", "AS2"]
    
    def set_grid(self, grid):
        """Set the grid object directly"""
        self.grid = grid
    
    def analyze_single_delivery(self, store: Position, customer: Position, strategy: str) -> Dict[str, Any]:
        """
        Analyze a single store->customer delivery with specific strategy.
        Returns detailed metrics.
        """
        tracemalloc.start()
        start_time = time.time()
        
        problem = DeliveryProblem(self.grid, store, customer)
        search = GenericSearch(problem, strategy=strategy)
        actions, cost, nodes_expanded = search.solve()
        
        elapsed = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        plan_str = ",".join(actions) if actions else "NO_PATH"
        
        return {
            'store': store,
            'customer': customer,
            'strategy': strategy,
            'plan': plan_str,
            'cost': cost,
            'nodes_expanded': nodes_expanded,
            'time_ms': elapsed * 1000,
            'memory_peak_kb': peak / 1024,
            'path_found': actions is not None,
            'path_length': len(actions) if actions else 0,
            'manhattan_distance': store.manhattan_distance(customer),
        }
    
    def analyze_all_pairs(self) -> Dict[str, Any]:
        """
        Analyze ALL store-customer pairs with ALL strategies.
        Returns comprehensive analysis data structure.
        """
        if not self.grid or not self.grid.stores or not self.grid.customers:
            return {'grid_info': {}, 'pairwise_analysis': {}}
        
        print(f"\n{'='*70}")
        print("DELIVERY ANALYSIS")
        print(f"{'='*70}")
        print(f"Grid: {self.grid.m}x{self.grid.n}")
        print(f"Stores: {len(self.grid.stores)}")
        print(f"Customers: {len(self.grid.customers)}")
        print(f"Strategies: {', '.join(self.strategies)}")
        print(f"{'='*70}")
        
        analysis_data = {
            'grid_info': {
                'dimensions': (self.grid.m, self.grid.n),
                'stores': self.grid.stores,
                'customers': self.grid.customers,
                'store_count': len(self.grid.stores),
                'customer_count': len(self.grid.customers),
            },
            'pairwise_analysis': {},
        }
        
        # Analyze each store-customer pair
        for store_idx, store in enumerate(self.grid.stores):
            for customer_idx, customer in enumerate(self.grid.customers):
                pair_key = f"store_{store_idx}_customer_{customer_idx}"
                
                # Get metrics for all strategies
                pair_metrics = {}
                for strategy in self.strategies:
                    metrics = self.analyze_single_delivery(store, customer, strategy)
                    pair_metrics[strategy] = metrics
                
                # Store in analysis data
                analysis_data['pairwise_analysis'][pair_key] = {
                    'store': store,
                    'customer': customer,
                    'store_idx': store_idx,
                    'customer_idx': customer_idx,
                    'manhattan_distance': store.manhattan_distance(customer),
                    'metrics_by_strategy': pair_metrics
                }
        
        # Generate assignments for each strategy
        analysis_data['assignments_by_strategy'] = {}
        for strategy in self.strategies:
            pure_assignments, pure_cost = self._pure_cost_assignment_for_strategy(analysis_data, strategy)
            balanced_assignments, balanced_cost, balanced_loads = self._balanced_assignment_for_strategy(analysis_data, strategy, max_load_diff=1)
            
            analysis_data['assignments_by_strategy'][strategy] = {
                'pure_cost': {
                    'assignments': pure_assignments,
                    'total_cost': pure_cost,
                    'store_loads': self._calculate_store_loads(pure_assignments),
                    'customer_count': len(pure_assignments)
                },
                'balanced': {
                    'assignments': balanced_assignments,
                    'total_cost': balanced_cost,
                    'store_loads': balanced_loads,
                    'customer_count': len(balanced_assignments)
                }
            }
        print(f"{'='*70}\n")
        print(analysis_data)
        print(f"{'='*70}\n")
        return analysis_data
    
    def _calculate_store_loads(self, assignments):
        """Calculate how many customers each store is assigned."""
        if not assignments:
            return []
        
        # Find max store index
        max_store_idx = max(assign['store_idx'] for assign in assignments)
        store_loads = [0] * (max_store_idx + 1)
        
        for assign in assignments:
            store_idx = assign['store_idx']
            store_loads[store_idx] += 1
        
        return store_loads
    
    def plan(self):
        """
        Main planning function.
        Returns analysis data structure with assignments for all strategies.
        """
        return self.analyze_all_pairs()
    
    def pure_cost_optimal_assignment(self, analysis_data):
        """
        Simple assignment: Each customer goes to the store with minimum cost.
        """
        if not analysis_data or 'pairwise_analysis' not in analysis_data:
            return [], 0

        num_customers = analysis_data['grid_info']['customer_count']
        assignments = []
        total_cost = 0

        for customer_idx in range(num_customers):
            best_store = None
            best_cost = float('inf')
            best_strategy = None

            # Look through all store-customer pairs for this customer
            for pair_key, pair_data in analysis_data['pairwise_analysis'].items():
                if pair_data['customer_idx'] == customer_idx:
                    store_idx = pair_data['store_idx']

                    # Find minimum cost strategy for this pair
                    for strategy, metrics in pair_data['metrics_by_strategy'].items():
                        if metrics['path_found'] and metrics['cost'] < best_cost:
                            best_cost = metrics['cost']
                            best_store = store_idx
                            best_strategy = strategy

            if best_store is not None:
                assignments.append({
                    'store_idx': best_store,
                    'customer_idx': customer_idx,
                    'cost': best_cost,
                    'strategy': best_strategy,
                })
                total_cost += best_cost

        return assignments, total_cost
    
    def balanced_cost_assignment(self, analysis_data, max_load_diff=1):
        """
        Cost-aware assignment with load balancing.
        """
        if not analysis_data or 'pairwise_analysis' not in analysis_data:
            return [], 0, []

        num_stores = analysis_data['grid_info']['store_count']
        num_customers = analysis_data['grid_info']['customer_count']

        # Prepare list of all possible assignments with costs
        candidate_assignments = []

        for pair_key, pair_data in analysis_data['pairwise_analysis'].items():
            store_idx = pair_data['store_idx']
            customer_idx = pair_data['customer_idx']

            # Find minimum cost for this pair
            min_cost = float('inf')
            best_strategy = None

            for strategy, metrics in pair_data['metrics_by_strategy'].items():
                if metrics['path_found'] and metrics['cost'] < min_cost:
                    min_cost = metrics['cost']
                    best_strategy = strategy

            if min_cost < float('inf'):
                candidate_assignments.append({
                    'store_idx': store_idx,
                    'customer_idx': customer_idx,
                    'cost': min_cost,
                    'strategy': best_strategy,
                })

        # Sort by cost (cheapest first)
        candidate_assignments.sort(key=lambda x: x['cost'])

        # Initialize
        store_loads = [0] * num_stores
        customer_assigned = [False] * num_customers
        assignments = []
        total_cost = 0

        # Assign customers (cheapest first, but respect load balance)
        for assignment in candidate_assignments:
            store_idx = assignment['store_idx']
            customer_idx = assignment['customer_idx']

            if customer_assigned[customer_idx]:
                continue
            
            # Check load balance constraint
            current_min_load = min(store_loads)
            if (store_loads[store_idx] + 1) <= (current_min_load + max_load_diff):
                store_loads[store_idx] += 1
                customer_assigned[customer_idx] = True
                assignments.append({
                    'store_idx': store_idx,
                    'customer_idx': customer_idx,
                    'cost': assignment['cost'],
                    'strategy': assignment['strategy'],
                })
                total_cost += assignment['cost']

        # Handle any unassigned customers
        for customer_idx in range(num_customers):
            if not customer_assigned[customer_idx]:
                # Find cheapest assignment for this customer
                cheapest = None
                for cand in candidate_assignments:
                    if cand['customer_idx'] == customer_idx:
                        if cheapest is None or cand['cost'] < cheapest['cost']:
                            cheapest = cand

                if cheapest:
                    store_idx = cheapest['store_idx']
                    store_loads[store_idx] += 1
                    assignments.append({
                        'store_idx': store_idx,
                        'customer_idx': customer_idx,
                        'cost': cheapest['cost'],
                        'strategy': cheapest['strategy'],
                    })
                    total_cost += cheapest['cost']

        return assignments, total_cost, store_loads
    
    def compare_assignment_strategies(self, analysis_data):
        """Compare different assignment strategies."""
        print(f"\n{'='*70}")
        print("ASSIGNMENT STRATEGIES COMPARISON")
        print(f"{'='*70}")

        # Pure cost optimal
        assignments1, cost1 = self.pure_cost_optimal_assignment(analysis_data)
        store_loads1 = [0] * analysis_data['grid_info']['store_count']
        for a in assignments1:
            store_loads1[a['store_idx']] += 1

        # Balanced assignment (max_diff=1)
        assignments2, cost2, loads2 = self.balanced_cost_assignment(analysis_data, max_load_diff=1)

        # Balanced assignment (max_diff=2)
        assignments3, cost3, loads3 = self.balanced_cost_assignment(analysis_data, max_load_diff=2)

        return {
            'pure_cost': {'assignments': assignments1, 'cost': cost1, 'loads': store_loads1},
            'balanced_1': {'assignments': assignments2, 'cost': cost2, 'loads': loads2},
            'balanced_2': {'assignments': assignments3, 'cost': cost3, 'loads': loads3}
        }
    
    def _pure_cost_assignment_for_strategy(self, analysis_data, search_strategy):
        """Pure cost assignment using a specific search strategy."""
        num_customers = analysis_data['grid_info']['customer_count']
        assignments = []
        total_cost = 0

        for customer_idx in range(num_customers):
            best_store = None
            best_cost = float('inf')

            # Find store with minimum cost using this search strategy
            for pair_key, pair_data in analysis_data['pairwise_analysis'].items():
                if pair_data['customer_idx'] == customer_idx:
                    if search_strategy in pair_data['metrics_by_strategy']:
                        metrics = pair_data['metrics_by_strategy'][search_strategy]
                        if metrics['path_found'] and metrics['cost'] < best_cost:
                            best_cost = metrics['cost']
                            best_store = pair_data['store_idx']

            if best_store is not None:
                assignments.append({
                    'store_idx': best_store,
                    'customer_idx': customer_idx,
                    'cost': best_cost,
                    'strategy': search_strategy
                })
                total_cost += best_cost

        return assignments, total_cost
    
    def _balanced_assignment_for_strategy(self, analysis_data, search_strategy, max_load_diff=1):
        """Balanced assignment using a specific search strategy."""
        num_stores = analysis_data['grid_info']['store_count']
        num_customers = analysis_data['grid_info']['customer_count']

        # Prepare candidate assignments
        candidates = []
        for pair_key, pair_data in analysis_data['pairwise_analysis'].items():
            if search_strategy in pair_data['metrics_by_strategy']:
                metrics = pair_data['metrics_by_strategy'][search_strategy]
                if metrics['path_found']:
                    candidates.append({
                        'store_idx': pair_data['store_idx'],
                        'customer_idx': pair_data['customer_idx'],
                        'cost': metrics['cost'],
                    })

        # Sort by cost and assign with load balancing
        candidates.sort(key=lambda x: x['cost'])
        store_loads = [0] * num_stores
        customer_assigned = [False] * num_customers
        assignments = []
        total_cost = 0

        for cand in candidates:
            store_idx = cand['store_idx']
            customer_idx = cand['customer_idx']

            if customer_assigned[customer_idx]:
                continue
            
            # Check load balance constraint
            current_min = min(store_loads)
            if (store_loads[store_idx] + 1) <= (current_min + max_load_diff):
                store_loads[store_idx] += 1
                customer_assigned[customer_idx] = True
                assignments.append({
                    'store_idx': store_idx,
                    'customer_idx': customer_idx,
                    'cost': cand['cost'],
                    'strategy': search_strategy
                })
                total_cost += cand['cost']

        # Handle unassigned customers
        for customer_idx in range(num_customers):
            if not customer_assigned[customer_idx]:
                # Fallback: cheapest available
                cheapest = None
                for cand in candidates:
                    if cand['customer_idx'] == customer_idx:
                        if cheapest is None or cand['cost'] < cheapest['cost']:
                            cheapest = cand

                if cheapest:
                    store_idx = cheapest['store_idx']
                    store_loads[store_idx] += 1
                    assignments.append({
                        'store_idx': store_idx,
                        'customer_idx': customer_idx,
                        'cost': cheapest['cost'],
                        'strategy': search_strategy
                    })
                    total_cost += cheapest['cost']

        return assignments, total_cost, store_loads
    
    def print_assignment_table(self, analysis_data):
        """Print assignment table for all strategies."""
        if 'assignments_by_strategy' not in analysis_data:
            print("No assignment data available")
            return
        
        print(f"\n{'='*70}")
        print("ASSIGNMENT TABLE - ALL STRATEGIES")
        print(f"{'='*70}")
        
        print(f"\n{'Strategy':<8} {'Type':<12} {'Total Cost':<12} {'Store Loads':<20} {'Customers':<10}")
        print("-" * 70)
        
        for strategy in self.strategies:
            if strategy in analysis_data['assignments_by_strategy']:
                data = analysis_data['assignments_by_strategy'][strategy]
                
                # Pure cost
                pure = data['pure_cost']
                loads_str = str(pure['store_loads'])
                print(f"{strategy:<8} {'Pure':<12} {pure['total_cost']:<12.1f} {loads_str:<20} {pure['customer_count']:<10}")
                
                # Balanced
                balanced = data['balanced']
                loads_str = str(balanced['store_loads'])
                print(f"{' ':<8} {'Balanced':<12} {balanced['total_cost']:<12.1f} {loads_str:<20} {balanced['customer_count']:<10}")
                
                # Cost difference if any
                if pure['total_cost'] > 0 and balanced['total_cost'] > pure['total_cost']:
                    diff = balanced['total_cost'] - pure['total_cost']
                    percent = (diff / pure['total_cost'] * 100)
                    print(f"{' ':<8} {'Δ':<12} {diff:<+12.1f} ({percent:+.1f}%)")
                
                print()  # Blank line