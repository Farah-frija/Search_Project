# Tests/test_delivery_planner.py
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from Delivery.Delivery_planner import DeliveryPlanner
from GridGenerator.gridGenerator import GridGenerator

def test_delivery_assignments():
    """Test delivery assignments for all strategies"""
    print("\n" + "="*70)
    print("DELIVERY ASSIGNMENT TEST")
    print("="*70)
    
    # Generate grid with multiple stores
    generator = GridGenerator()
    grid, _, _ = generator.gen_grid(min_stores=2, max_stores=3, min_customers=4, max_customers=6,min_obstacle_prob=0.02)
    
    print(f"Grid: {grid.m}x{grid.n}")
    print(f"Stores: {[str(s) for s in grid.stores]}")
    print(f"Customers: {[str(c) for c in grid.customers]}")
    print("="*70)
    
    planner = DeliveryPlanner(grid)
    
    # Get analysis with assignments
    print("\nRunning analysis...")
    analysis_data = planner.plan()
    
    # Print assignment table
    planner.print_assignment_table(analysis_data)
    
    # Also show comparison
    print("\n" + "="*70)
    print("OVERALL COMPARISON")
    print("="*70)
    
    comparison = planner.compare_assignment_strategies(analysis_data)
    
    print(f"\n{'Strategy':<15} {'Total Cost':<12} {'Store Loads':<20} {'Imbalance':<10}")
    print("-" * 65)
    
    pure = comparison['pure_cost']
    pure_imbalance = max(pure['loads']) - min(pure['loads']) if pure['loads'] else 0
    print(f"{'Pure Cost':<15} {pure['cost']:<12.1f} {str(pure['loads']):<20} {pure_imbalance:<10}")
    
    bal1 = comparison['balanced_1']
    bal1_imbalance = max(bal1['loads']) - min(bal1['loads']) if bal1['loads'] else 0
    print(f"{'Balanced (1)':<15} {bal1['cost']:<12.1f} {str(bal1['loads']):<20} {bal1_imbalance:<10}")
    
    bal2 = comparison['balanced_2']
    bal2_imbalance = max(bal2['loads']) - min(bal2['loads']) if bal2['loads'] else 0
    print(f"{'Balanced (2)':<15} {bal2['cost']:<12.1f} {str(bal2['loads']):<20} {bal2_imbalance:<10}")
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)
    
    return analysis_data, comparison

test_delivery_assignments()