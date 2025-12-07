import sys
import os
# test_imports.py
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.join(current_dir, "core")
sys.path.insert(0, core_path)
from DataStructure.Position import Position

from DataStructure.Grid import Grid
from Delivery.Delivery_planner import DeliveryPlanner
from GridGenerator.gridGenerator import GridGenerator
from Parsers.InputParser import parse_input_with_stores
from Search.Delivery_problem import DeliveryProblem
from Search.Generic_search import GenericSearch
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import uuid

from .models import *



router = APIRouter()

# In-memory storage (replace with Redis/DB in production)
grid_store = {}
search_cache = {}

@router.post("/grid/generate", response_model=Dict[str, Any])
async def generate_grid(config: GridConfig):
    """Generate a new grid with given configuration"""
    try:
        grid_id = str(uuid.uuid4())
        
        # Generate grid using existing GridGenerator
    
        
        generator = GridGenerator(seed=config.seed)
        init_str, traffic_str, stores = generator.generate_grid(
            min_m=config.width,
            max_m=config.width,
            min_n=config.height,
            max_n=config.height,
            min_stores=config.min_stores,
            max_stores=config.max_stores,
            min_customers=config.min_customers,
            max_customers=config.max_customers,
            min_tunnels=1 if config.tunnel_density > 0 else 0,
            max_tunnel_prob=config.tunnel_density,
            min_obstacle_prob=config.obstacle_density,
            max_obstacle_prob=config.obstacle_density,
            min_traffic=config.min_traffic,
            max_traffic=config.max_traffic
        )
        
        # Parse grid
        grid = parse_input_with_stores(init_str, traffic_str, stores)
        
        # Store grid data
        grid_data = {
            "id": grid_id,
            "config": config.dict(),
            "grid": {
                "width": grid.m,
                "height": grid.n,
                "stores": [{"x": s.x, "y": s.y} for s in grid.stores],
                "customers": [{"x": c.x, "y": c.y} for c in grid.customers],
                "tunnels": [],
                "traffic_edges": []
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Add tunnels
        seen_tunnels = set()
        for entrance, exit_pos in grid.tunnels.items():
            pair = tuple(sorted([(entrance.x, entrance.y), (exit_pos.x, exit_pos.y)]))
            if pair not in seen_tunnels:
                grid_data["grid"]["tunnels"].append({
                    "entrance": {"x": entrance.x, "y": entrance.y},
                    "exit": {"x": exit_pos.x, "y": exit_pos.y}
                })
                seen_tunnels.add(pair)
        
        # Add traffic edges
        for edge, cost in grid.traffic.items():
            grid_data["grid"]["traffic_edges"].append({
                "from": {"x": edge.pos1.x, "y": edge.pos1.y},
                "to": {"x": edge.pos2.x, "y": edge.pos2.y},
                "cost": cost
            })
        
        grid_store[grid_id] = grid_data
        
        return {
            "grid_id": grid_id,
            "grid": grid_data["grid"],
            "metadata": {
                "stores_count": len(grid.stores),
                "customers_count": len(grid.customers),
                "tunnels_count": len(seen_tunnels),
                "obstacles_count": sum(1 for e in grid.traffic.values() if e == 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grid generation failed: {str(e)}")

@router.get("/grid/{grid_id}")
async def get_grid(grid_id: str):
    """Get a specific grid by ID"""
    if grid_id not in grid_store:
        raise HTTPException(status_code=404, detail="Grid not found")
    return grid_store[grid_id]

@router.get("/grids")
async def list_grids(limit: int = 10, offset: int = 0):
    """List all available grids"""
    grids = list(grid_store.values())[offset:offset+limit]
    return {
        "grids": grids,
        "total": len(grid_store),
        "limit": limit,
        "offset": offset
    }

@router.post("/search")
async def search_path(request:SearchRequest):
    """Find path from store to customer using specified algorithm"""
    print(request)
    try:
        start_time = datetime.now()
        
        # Get or generate grid
        if request.grid_id:
            if request.grid_id not in grid_store:
                raise HTTPException(status_code=404, detail="Grid not found")
            grid_data = grid_store[request.grid_id]
       
        # Convert to Grid object
        grid = Grid(grid_data["grid"]["width"], grid_data["grid"]["height"])
        
        # Add stores
        for store in grid_data["grid"]["stores"]:
            print("dkhal f stores")
            grid.add_store(Position(store["x"], store["y"]))
        print("khrj m stores")
        # Add customers
        for customer in grid_data["grid"]["customers"]:
            print("dkhal f stores")
            grid.add_customer(Position(customer["x"], customer["y"]))
        print("khrj m stores")
        # Add tunnels
        for tunnel in grid_data["grid"]["tunnels"]:
            entrance = Position(tunnel["entrance"]["x"], tunnel["entrance"]["y"])
            exit_pos = Position(tunnel["exit"]["x"], tunnel["exit"]["y"])
            grid.add_tunnel(entrance, exit_pos)
        print("khrj m tunnel")
        # Add traffic
        for edge in grid_data["grid"]["traffic_edges"]:
            pos1 = Position(edge["from"]["x"], edge["from"]["y"])
            pos2 = Position(edge["to"]["x"], edge["to"]["y"])
            grid.set_traffic(pos1, pos2, edge["cost"])
        print("khrj m edge")
        
        # Create positions
        store_pos = Position(request.store_position.x, request.store_position.y)
        customer_pos = Position(request.customer_position.x, request.customer_position.y)
        print("snaa pos")
        # Add traffic
        # FIXED: Pass arguments as keyword arguments
        problem = DeliveryProblem(
            grid, store_pos, customer_pos # Check the actual parameter name in DeliveryProblem
        )
        print("problem")
        # Alternative: Check what parameters DeliveryProblem expects
        # Common parameter names might be:
        # problem = DeliveryProblem(
        #     grid=grid,
        #     start=store_pos,
        #     goal=customer_pos
        # )
        # OR
        # problem = DeliveryProblem(
        #     grid=grid,
        #     start_position=store_pos,
        #     delivery_positions=[customer_pos]  # If it expects a list
        # )
        
        # Run search
        search = GenericSearch(
          problem,  # Also fix this if GenericSearch expects keyword args
            strategy=request.algorithm.value.upper()
            #heuristic_name=request.heuristic.value
        )
        print("gense")
        path, cost, nodes = search.solve()
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        print("gense")
        # Convert path to positions
        positions = []
        if path:
            current = store_pos
            positions.append(Positioni(x=current.x, y=current.y))
            for action in path:
                if action == "up":
                    current = Position(current.x, current.y + 1)
                elif action == "down":
                    current = Position(current.x, current.y - 1)
                elif action == "left":
                    current = Position(current.x - 1, current.y)
                elif action == "right":
                    current = Position(current.x + 1, current.y)
                elif action == "tunnel":
                    current = grid.get_tunnel_exit(current)
                positions.append(Positioni(x=current.x, y=current.y))
        
        return SearchResponse(
            success=path is not None,
            path=path,
            positions=positions,
            total_cost=cost if path else 0.0,
            nodes_expanded=nodes,
            execution_time_ms=execution_time,
            grid_data=grid_data,
            message="Path found successfully" if path else "No path found"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/search/compare")
async def compare_algorithms(
    grid_id: str,
    store_position: Positioni,
    customer_position: Positioni,
    algorithms: List[SearchAlgorithm] = None
):
    """Compare multiple algorithms for the same search"""
    try:
        if algorithms is None:
            algorithms = list(SearchAlgorithm)
        
        results = []
        for algorithm in algorithms:
            request = SearchRequest(
                grid_id=grid_id,
                store_position=store_position,
                customer_position=customer_position,
                algorithm=algorithm
            )
            response = await search_path(request)
            
            results.append({
                "algorithm": algorithm.value,
                "success": response.success,
                "total_cost": response.total_cost,
                "nodes_expanded": response.nodes_expanded,
                "execution_time_ms": response.execution_time_ms,
                "path_length": len(response.path) if response.path else 0
            })
        
        # Sort by cost (successful searches first)
        results.sort(key=lambda x: (not x["success"], x["total_cost"]))
        
        return {
            "comparison": results,
            "best_algorithm": results[0]["algorithm"] if results else None,
            "grid_id": grid_id,
            "store": store_position.dict(),
            "customer": customer_position.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.post("/delivery/plan")
async def plan_deliveries(request: AssignmentRequest):
    """Plan deliveries for multiple packages"""
    try:
        if request.grid_id not in grid_store:
            raise HTTPException(status_code=404, detail="Grid not found")
        
        grid_data = grid_store[request.grid_id]
        
        # Use DeliveryPlanner
       
        
        # Convert grid data to Grid object (similar to search endpoint)
        grid = Grid(grid_data["grid"]["width"], grid_data["grid"]["height"])
        
        for store in grid_data["grid"]["stores"]:
            grid.add_store(Position(store["x"], store["y"]))
        
        for customer in grid_data["grid"]["customers"]:
            grid.add_customer(Position(customer["x"], customer["y"]))
        
        for tunnel in grid_data["grid"]["tunnels"]:
            entrance = Position(tunnel["entrance"]["x"], tunnel["entrance"]["y"])
            exit_pos = Position(tunnel["exit"]["x"], tunnel["exit"]["y"])
            grid.add_tunnel(entrance, exit_pos)
        
        for edge in grid_data["grid"]["traffic_edges"]:
            pos1 = Position(edge["from"]["x"], edge["from"]["y"])
            pos2 = Position(edge["to"]["x"], edge["to"]["y"])
            grid.set_traffic(pos1, pos2, edge["cost"])
        
        # Run planner
        planner = DeliveryPlanner(grid)
        analysis = planner.analyze_all_pairs()
        
        # Get assignments based on strategy
        if request.assignment_strategy == "pure_cost":
            assignments, total_cost = planner.pure_cost_optimal_assignment(analysis)
            store_loads = planner._calculate_store_loads(assignments)
        else:  # balanced
            assignments, total_cost, store_loads = planner.balanced_cost_assignment(
                analysis, max_load_diff=request.max_load_diff
            )
        
        # Format response
        assignments_dict = {}
        for store_idx in range(len(grid.stores)):
            customer_ids = [
                a["customer_idx"] for a in assignments 
                if a["store_idx"] == store_idx
            ]
            assignments_dict[f"store_{store_idx}"] = customer_ids
        
        store_loads_dict = {
            f"store_{i}": load for i, load in enumerate(store_loads)
        }
        
        return {
            "success": True,
            "assignments": assignments_dict,
            "total_cost": total_cost,
            "store_loads": store_loads_dict,
            "metrics": {
                "stores_count": len(grid.stores),
                "customers_count": len(grid.customers),
                "assignment_strategy": request.assignment_strategy,
                "max_load_diff": request.max_load_diff
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delivery planning failed: {str(e)}")

##################################################################################
@router.post("/delivery/plan2")
async def plan_deliveries2(request: AssignmentRequest):
    """Plan deliveries with comprehensive strategy comparison"""
    try:
        if request.grid_id not in grid_store:
            raise HTTPException(status_code=404, detail="Grid not found")
        
        grid_data = grid_store[request.grid_id]
        
        # Use DeliveryPlanner
       
        
        # Convert grid data to Grid object (similar to search endpoint)
        grid = Grid(grid_data["grid"]["width"], grid_data["grid"]["height"])
        
        for store in grid_data["grid"]["stores"]:
            grid.add_store(Position(store["x"], store["y"]))
        
        for customer in grid_data["grid"]["customers"]:
            grid.add_customer(Position(customer["x"], customer["y"]))
        
        for tunnel in grid_data["grid"]["tunnels"]:
            entrance = Position(tunnel["entrance"]["x"], tunnel["entrance"]["y"])
            exit_pos = Position(tunnel["exit"]["x"], tunnel["exit"]["y"])
            grid.add_tunnel(entrance, exit_pos)
        
        for edge in grid_data["grid"]["traffic_edges"]:
            pos1 = Position(edge["from"]["x"], edge["from"]["y"])
            pos2 = Position(edge["to"]["x"], edge["to"]["y"])
            grid.set_traffic(pos1, pos2, edge["cost"])

        # Run planner with comparison
        planner = DeliveryPlanner(grid)
        analysis = planner.analyze_all_pairs()
        
        # Generate comprehensive comparison
        comparison = []
        
        for strategy in planner.strategies:
            # Get assignments for this strategy
            if request.assignment_strategy == "pure_cost":
                assignments, total_cost = planner._pure_cost_assignment_for_strategy(
                    analysis, strategy
                )
                store_loads = planner._calculate_store_loads(assignments)
            else:  # balanced
                assignments, total_cost, store_loads = planner._balanced_assignment_for_strategy(
                    analysis, strategy, max_load_diff=request.max_load_diff
                )
            
            # Enrich assignments with path details
            detailed_assignments = []
            for assignment in assignments:
                pair_key = f"store_{assignment['store_idx']}_customer_{assignment['customer_idx']}"
                pair_data = analysis['pairwise_analysis'][pair_key]
                metrics = pair_data['metrics_by_strategy'][strategy]
                
                detailed_assignments.append({
                    "store_idx": assignment['store_idx'],
                    "customer_idx": assignment['customer_idx'],
                    "store_position": {
                        "x": pair_data['store'].x,
                        "y": pair_data['store'].y
                    },
                    "customer_position": {
                        "x": pair_data['customer'].x,
                        "y": pair_data['customer'].y
                    },
                    "path_cost": metrics['cost'],
                    "path_found": metrics['path_found'],
                    "path_actions": metrics['plan'] if metrics['plan'] != "NO_PATH" else None,
                    "nodes_expanded": metrics['nodes_expanded'],
                    "time_ms": metrics['time_ms'],
                    "memory_kb": metrics['memory_peak_kb'],
                    "path_length": metrics['path_length']
                })
            
            # Group assignments by store
            store_assignments = {}
            for store_idx in range(len(grid.stores)):
                store_customers = [
                    a for a in detailed_assignments 
                    if a["store_idx"] == store_idx
                ]
                store_assignments[f"store_{store_idx}"] = {
                    "store_position": store_customers[0]["store_position"] if store_customers else None,
                    "customer_count": len(store_customers),
                    "total_store_cost": sum(c["path_cost"] for c in store_customers),
                    "customers": [
                        {
                            "customer_idx": c["customer_idx"],
                            "position": c["customer_position"],
                            "path_cost": c["path_cost"],
                            "path_actions": c["path_actions"],
                            "path_length": c["path_length"],
                            "time_ms": c["time_ms"],
                            "nodes_expanded": c["nodes_expanded"]
                        }
                        for c in store_customers
                    ]
                }
            
            # Calculate aggregate metrics
            all_paths = [a for a in detailed_assignments if a["path_found"]]
            
            comparison.append({
                "strategy": strategy,
                "summary": {
                    "total_cost": total_cost,
                    "total_assignments": len(assignments),
                    "successful_paths": len(all_paths),
                    "failed_paths": len(assignments) - len(all_paths),
                    "average_cost_per_delivery": total_cost / len(all_paths) if all_paths else 0,
                    "average_time_ms": sum(a["time_ms"] for a in all_paths) / len(all_paths) if all_paths else 0,
                    "average_nodes_expanded": sum(a["nodes_expanded"] for a in all_paths) / len(all_paths) if all_paths else 0,
                    "total_time_ms": sum(a["time_ms"] for a in detailed_assignments),
                    "total_nodes_expanded": sum(a["nodes_expanded"] for a in detailed_assignments)
                },
                "store_loads": {
                    f"store_{i}": {
                        "load": load,
                        "percentage": (load / len(assignments) * 100) if assignments else 0
                    }
                    for i, load in enumerate(store_loads)
                },
                "store_assignments": store_assignments,
                "detailed_assignments": detailed_assignments,
                "metrics_by_complexity": {
                    "simple_paths": len([a for a in all_paths if a["path_length"] <= 5]),
                    "medium_paths": len([a for a in all_paths if 5 < a["path_length"] <= 15]),
                    "complex_paths": len([a for a in all_paths if a["path_length"] > 15]),
                    "shortest_path": min((a["path_length"] for a in all_paths), default=0),
                    "longest_path": max((a["path_length"] for a in all_paths), default=0)
                }
            })
        
        # Sort strategies by total cost (most efficient first)
        comparison.sort(key=lambda x: x["summary"]["total_cost"])
        
        # Find the best strategy based on combined metrics
        best_strategy = min(
            comparison,
            key=lambda x: (
                x["summary"]["total_cost"] * 0.5 +  # 50% weight to cost
                x["summary"]["average_time_ms"] * 0.2 +  # 20% to speed
                x["summary"]["average_nodes_expanded"] * 0.1 +  # 10% to memory efficiency
                (x["summary"]["failed_paths"] * 1000) * 0.2  # 20% penalty for failures
            )
        )["strategy"]
        
        aa= {
            "success": True,
            "assignment_strategy": request.assignment_strategy,
            "max_load_diff": request.max_load_diff,
            "best_overall_strategy": best_strategy,
            "strategy_comparison": comparison,
            "grid_metrics": {
                "stores_count": len(grid.stores),
                "customers_count": len(grid.customers),
                "total_possible_pairs": len(grid.stores) * len(grid.customers)
            },
            "recommendations": _generate_recommendations(comparison)
        }
        print("ooooooooooooooooooooooooooooooooooooooooooooooo")
        print(aa)
        print('oooooooooooooooooooooooooooooooooooooo')
        return aa
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delivery planning failed: {str(e)}")


def _generate_recommendations(comparison):
    """Generate actionable insights from the comparison"""
    if not comparison:
        return []
    
    recommendations = []
    
    # Cost-focused recommendation
    cheapest = min(comparison, key=lambda x: x["summary"]["total_cost"])
    recommendations.append({
        "type": "cost_efficiency",
        "strategy": cheapest["strategy"],
        "message": f"{cheapest['strategy']} is the most cost-efficient with total cost {cheapest['summary']['total_cost']:.1f}",
        "savings_percent": ((comparison[0]["summary"]["total_cost"] - cheapest["summary"]["total_cost"]) / 
                           comparison[0]["summary"]["total_cost"] * 100) if comparison[0]["summary"]["total_cost"] > 0 else 0
    })
    
    # Speed-focused recommendation
    fastest = min(comparison, key=lambda x: x["summary"]["average_time_ms"])
    recommendations.append({
        "type": "speed",
        "strategy": fastest["strategy"],
        "message": f"{fastest['strategy']} is the fastest with average {fastest['summary']['average_time_ms']:.2f} ms per path",
        "time_savings_percent": ((comparison[0]["summary"]["average_time_ms"] - fastest["summary"]["average_time_ms"]) / 
                                comparison[0]["summary"]["average_time_ms"] * 100) if comparison[0]["summary"]["average_time_ms"] > 0 else 0
    })
    
    # Reliability recommendation
    most_reliable = max(comparison, key=lambda x: x["summary"]["successful_paths"])
    if most_reliable["summary"]["failed_paths"] == 0:
        recommendations.append({
            "type": "reliability",
            "strategy": most_reliable["strategy"],
            "message": f"{most_reliable['strategy']} found paths for all assignments",
            "reliability": "100%"
        })
    
    # Balance recommendation
    balanced_loads = []
    for strategy_data in comparison:
        loads = [store["load"] for store in strategy_data["store_loads"].values()]
        if loads:
            load_diff = max(loads) - min(loads)
            balanced_loads.append((strategy_data["strategy"], load_diff))
    
    if balanced_loads:
        most_balanced = min(balanced_loads, key=lambda x: x[1])
        recommendations.append({
            "type": "load_balance",
            "strategy": most_balanced[0],
            "message": f"{most_balanced[0]} has the most balanced store loads (max difference: {most_balanced[1]})",
            "load_imbalance": most_balanced[1]
        })
    
    return recommendations

####################################################
@router.post("/search/animate")
async def animate_search(request):
    """Stream search animation frames"""
    async def generate_frames():
        # This would yield SSE frames for real-time animation
        # Implementation depends on how you want to stream
        yield f"data: {json.dumps({'type': 'start', 'message': 'Starting search...'})}\n\n"
        
        # Simulate search steps
        for i in range(10):
            await asyncio.sleep(0.1)
            yield f"data: {json.dumps({'type': 'progress', 'step': i, 'message': f'Step {i}'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'complete', 'message': 'Search complete'})}\n\n"
    
    return StreamingResponse(
        generate_frames(),
        media_type="text/event-stream"
    )