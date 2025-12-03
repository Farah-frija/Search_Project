# **Delivery Route Planning System - Technical Readme**

## **📋 Project Overview**
A comprehensive AI-based delivery route planning system implementing multiple search algorithms for optimal package delivery in grid-based environments with obstacles, tunnels, and variable traffic costs.

## **🏗️ System Architecture**

### **Core Components**

```
Delivery-Route-Planner/
├── 📁 DataStructure/           # Core data models
│   ├── Position.py           # 2D coordinate system
│   ├── Grid.py              # Grid representation
│   ├── Edge.py              # Graph edges with traffic
│   ├── DeliveryState.py     # Search state representation
│   └── Node.py             # Search tree nodes
├── 📁 Search/                # Search algorithms
│   ├── Search_problem.py    # Abstract search interface
│   ├── Delivery_problem.py  # Concrete delivery problem
│   ├── Generic_search.py    # Multiple search strategies
│   ├── Heuristics.py        # Admissible heuristics
│   └── Tree_node.py         # Search tree implementation
├── 📁 GridGenerator/         # Random grid generation
│   └── gridGenerator.py     # Configurable grid generator
├── 📁 Parsers/              # Input parsing
│   ├── InputParser.py       # Main parser
│   ├── InitialStateParser.py
│   └── TrafficParser.py
├── 📁 Delivery/             # High-level planning
│   ├── Delivery_planner.py  # Multi-package assignment
│   └── Delivery_Search.py   # Search interface wrapper
├── 📁 Tests/                # Test suites
├── 📁 Visualization/        # Interactive console
│   └── InteractiveConsole.py
└── 📁 Analysis/            # Performance analysis
```

## **🔍 Search Algorithms Implemented**

### **Uninformed Search**
| Algorithm | Complexity | Optimality | Completeness | Use Case |
|-----------|------------|------------|--------------|----------|
| **BFS** | O(b^d) | ✓ Optimal | ✓ Complete | Shortest path (unit cost) |
| **DFS** | O(b^m) | ✗ Not optimal | ✓ Complete | Memory-efficient exploration |
| **Iterative Deepening** | O(b^d) | ✓ Optimal | ✓ Complete | Space-efficient BFS |
| **Uniform Cost** | O(b^(C*/ε)) | ✓ Optimal | ✓ Complete | Variable cost paths |

### **Informed Search**
| Algorithm | Heuristic | Optimality | Use Case |
|-----------|-----------|------------|----------|
| **Greedy (GR1/GR2)** | Manhattan/Diagonal | ✗ Not optimal | Quick exploration |
| **A* (AS1/AS2)** | Manhattan/Diagonal | ✓ Optimal | Optimal pathfinding |

### **Heuristics Available**
- **Manhattan Distance**: Admissible for 4-direction movement
- **Diagonal Distance**: Chebyshev distance (admissible)
- **Zero Heuristic**: Fallback (guarantees optimality)
- **Euclidean**: Not admissible (for testing)

## **📊 Problem Representation**

### **State Space**
```
State = {
    current_position: Position(x, y),
    target_position: Position(x, y),
    cost_so_far: float,
    path_taken: List[Action]
}
```

### **Action Space**
```
Actions = {
    "up": Move ↑ (cost = traffic),
    "down": Move ↓ (cost = traffic),
    "left": Move ← (cost = traffic),
    "right": Move → (cost = traffic),
    "tunnel": Teleport (cost = Manhattan distance)
}
```

### **Grid Elements**
```
Grid = {
    dimensions: (m, n),
    stores: List[Position],
    customers: List[Position],
    traffic: Dict[Edge → int],
    tunnels: Dict[Position → Position]
}
```

## **🎯 Key Features**

### **1. Dynamic Grid Generation**
```python
# Configurable parameters
GridGenerator.generate_grid(
    min_m=5, max_m=15,          # Grid size range
    min_stores=1, max_stores=5, # Delivery points
    min_customers=3, max_customers=10,
    obstacle_prob=0.1,          # Blocked edges (0-30%)
    tunnel_prob=0.2,            # Teleport tunnels
    min_traffic=1, max_traffic=4 # Edge costs
)
```

### **2. Multi-Algorithm Comparison**
```python
# Compare 8 search strategies simultaneously
strategies = ["BF", "DF", "ID", "UC", "GR1", "GR2", "AS1", "AS2"]
results = planner.compare_algorithms(store, customer)
```

### **3. Delivery Assignment**
```python
# Multi-package assignment strategies
assignments = planner.plan_deliveries(
    strategy="balanced",    # Pure cost vs load balancing
    max_load_diff=2         # Maximum store load difference
)
```

### **4. Interactive Visualization**
```python
# Real-time console visualization
visualizer.display_grid(
    show_traffic=True,      # Display edge costs
    show_visited=True,      # Highlight explored nodes
    show_frontier=True,     # Show frontier nodes
    animate_search=True,    # Step-by-step animation
    speed=0.1               # Animation delay
)
```

## **⚙️ Technical Specifications**

### **Performance Metrics**
- **Time Complexity**: O(b^d) to O(b^(C*/ε))
- **Space Complexity**: O(b^d) to O(bm)
- **Optimality Guarantees**: A* and UCS are optimal
- **Completeness**: All algorithms are complete

### **Memory Management**
- **State Hashing**: Efficient state comparison using `__hash__` and `__eq__`
- **Priority Queues**: Heap-based for UCS, A*, Greedy
- **Explored Sets**: Prevents redundant exploration

### **Edge Cases Handled**
1. **Unreachable customers**: Returns "NO_PATH"
2. **Obstacle clusters**: Algorithms find detours
3. **Tunnel cycles**: Detected and handled
4. **Multiple optimal paths**: Returns first found
5. **Zero-traffic edges**: Treated as obstacles

## **🔬 Testing Framework**

### **Unit Tests**
```python
# Test categories
- test_grid_generation.py    # Grid validity
- test_search_basic.py       # Algorithm correctness
- test_delivery_assignments.py # Multi-package logic
- test_obstacles_tunnels.py  # Edge case handling
```

### **Validation Checks**
1. **Grid Connectivity**: All stores can reach all customers
2. **Cost Admissibility**: Heuristics never overestimate
3. **Path Validity**: All returned paths are traversable
4. **Cost Consistency**: Path cost = sum of edge costs

## **📈 Performance Analysis**

### **Metrics Tracked**
```python
metrics = {
    'nodes_expanded': int,      # Search efficiency
    'path_cost': float,         # Solution quality
    'execution_time_ms': float, # Algorithm speed
    'memory_peak_kb': float,    # Space usage
    'path_length': int,         # Number of steps
}
```

### **Algorithm Comparison Matrix**
| Algorithm | Time | Space | Optimal | Best For |
|-----------|------|-------|---------|----------|
| **BFS** | High | High | ✓ | Small grids, unit cost |
| **DFS** | High | Low | ✗ | Deep paths, memory limits |
| **UCS** | High | High | ✓ | Variable costs |
| **A*** | Medium | Medium | ✓ | Most practical cases |
| **Greedy** | Low | Low | ✗ | Quick solutions |

## **🚀 Quick Start**

### **1. Basic Usage**
```python
from Delivery.Delivery_Search import DeliverySearch

# Generate random grid
grid, init_str, traffic_str = DeliverySearch.GenGrid()

# Find path from store to customer
result = DeliverySearch.path(grid, store_pos, customer_pos, "AS1")
# Format: "plan;cost;nodesExpanded"
```

### **2. Interactive Console**
```bash
python InteractiveConsole.py
# Follow menu prompts for full control
```

### **3. Custom Grid Generation**
```python
from GridGenerator.gridGenerator import GridGenerator

generator = GridGenerator(seed=42)  # Reproducible
grid = generator.gen_grid(
    min_m=10, max_m=10,
    min_stores=3, max_stores=3,
    min_customers=8, max_customers=8,
    obstacle_prob=0.15,
    tunnel_prob=0.25
)
```

## **🛠️ Configuration Options**

### **Search Parameters**
```python
# In InteractiveConsole.py user_settings
{
    'default_strategy': 'AS1',      # Default algorithm
    'animate_search': False,        # Real-time visualization
    'animation_speed': 0.1,         # Seconds per step
    'show_search_stats': True,      # Performance metrics
}
```

### **Visualization Settings**
```python
{
    'color_mode': 'full',           # 'full', 'limited', or 'none'
    'symbol_mode': 'unicode',       # 'unicode' or 'ascii'
    'show_traffic': False,          # Display edge costs
    'highlight_path': True,         # Color the solution path
    'show_visited': True,           # Show explored nodes
    'show_frontier': False,         # Show frontier nodes
}
```

## **📚 API Reference**

### **Core Classes**

#### **GridGenerator**
```python
class GridGenerator:
    def generate_grid(**kwargs) -> (str, str, List[Position])
    def gen_grid(**kwargs) -> (Grid, str, str)
```

#### **GenericSearch**
```python
class GenericSearch:
    def __init__(problem, strategy="BF", heuristic='manhattan')
    def solve() -> (List[str], float, int)  # (path, cost, nodes)
```

#### **DeliveryPlanner**
```python
class DeliveryPlanner:
    def plan() -> Dict  # Complete delivery analysis
    def analyze_all_pairs() -> Dict  # Store-customer metrics
```

### **Data Structures**

#### **Position**
```python
class Position:
    def __init__(x: int, y: int)
    def manhattan_distance(other: Position) -> int
    # Supports hashing and equality
```

#### **Grid**
```python
class Grid:
    def __init__(m: int, n: int)
    def add_store(pos: Position)
    def add_customer(pos: Position)
    def set_traffic(pos1: Position, pos2: Position, level: int)
    def is_blocked(pos1: Position, pos2: Position) -> bool
    def get_tunnel_exit(pos: Position) -> Optional[Position]
```

## **🔍 Advanced Features**

### **Tunnel Cost Calculation**
```
Tunnel cost = Manhattan distance between entrance and exit
Rationale: Represents "underground travel" proportional to distance
Usage: Can bypass obstacles but may not always be optimal
```

### **Obstacle Representation**
```
Traffic level = 0 → Obstacle (blocked edge)
Traffic level > 0 → Traversable edge with cost
Implementation: Filtered in get_successors() method
```

### **Multi-Package Optimization**
```
Strategies:
1. Pure cost: Each customer to cheapest store
2. Balanced: Load balancing with cost consideration
3. Hybrid: Configurable trade-off between cost and balance
```

## **📊 Output Formats**

### **Search Result**
```
"up,right,down,tunnel,left;15.0;42"
↑ Path actions separated by commas
↑ Total cost
↑ Nodes expanded during search
```

### **Grid Representation**
```
Initial state: "m;n;P;S;x1,y1,x2,y2,...;tx1,ty1,tx2,ty2,..."
Traffic data: "x1,y1,x2,y2,cost;x3,y3,x4,y4,cost;..."
```

## **🧪 Testing & Validation**

Run complete test suite:
```bash
python -m pytest Tests/ -v
```

Individual test modules:
```bash
python Tests/test_search_basic.py
python Tests/test_grid_generator.py
python Tests/test_delivery_assignments.py
```

## **📈 Performance Tuning**

### **For Large Grids**
```python
# Use A* with admissible heuristics
planner = DeliveryPlanner(grid)
result = planner.analyze_single_delivery(store, customer, "AS1")

# Enable memory-efficient settings
settings = {
    'show_visited': False,
    'show_frontier': False,
    'compress_display': True
}
```

### **For Real-time Visualization**
```python
# Reduce animation delay
visualizer.user_settings['animation_speed'] = 0.05

# Simplify display
visualizer.user_settings['symbol_mode'] = 'ascii'
visualizer.user_settings['color_mode'] = 'limited'
```

## **⚠️ Common Issues & Solutions**

### **"No path found"**
- Check obstacle density (reduce `obstacle_prob`)
- Ensure tunnels connect disconnected areas
- Verify store/customer positions are valid

### **Slow Performance**
- Use A* instead of BFS/UCS for large grids
- Reduce grid size or obstacle density
- Disable visualization for batch processing

### **Memory Errors**
- Use IDS for memory-constrained environments
- Reduce `max_stores` and `max_customers`
- Enable `compress_display` in visualization

## **🚀 Future Enhancements**

### **Planned Features**
1. **Bidirectional Search**: Faster pathfinding for large grids
2. **Time-dependent Traffic**: Dynamic edge costs
3. **Multi-Agent Coordination**: Multiple delivery trucks
4. **Machine Learning Heuristics**: Learned cost estimators
5. **Web Interface**: Browser-based visualization

### **Research Extensions**
- **Hierarchical A***: Multi-level pathfinding
- **Anytime Algorithms**: Progressive refinement
- **Monte Carlo Tree Search**: Stochastic environments
- **Reinforcement Learning**: Adaptive pathfinding

## **📄 License & Attribution**

This project implements standard search algorithms for educational purposes. Algorithms are based on Russell & Norvig "Artificial Intelligence: A Modern Approach".

### **Algorithm Sources**
- BFS/DFS: Classic graph traversal
- A*/UCS: Hart, Nilsson, Raphael (1968)
- Heuristics: Common admissible heuristics for grid worlds

---



*For questions or contributions, please refer to the project repository.*
