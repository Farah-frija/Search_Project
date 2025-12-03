from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class SearchAlgorithm(str, Enum):
    BFS = "bf"
    DFS = "df"
    IDS = "id"
    UCS = "uc"
    GREEDY1 = "gr1"
    GREEDY2 = "gr2"
    ASTAR1 = "as1"
    ASTAR2 = "as2"

class Heuristic(str, Enum):
    MANHATTAN = "manhattan"
    EUCLIDEAN = "euclidean"
    DIAGONAL = "diagonal"
    ZERO = "zero"

class Positioni(BaseModel):
    x: int
    y: int

class GridConfig(BaseModel):
    width: int = 10
    height: int = 10
    min_stores: int = 2
    max_stores: int = 4
    min_customers: int = 5
    max_customers: int = 8
    obstacle_density: float = 0.15
    tunnel_density: float = 0.2
    min_traffic: int = 1
    max_traffic: int = 4
    seed: Optional[int] = None

class SearchRequest(BaseModel):
    grid_id: Optional[str] = None
    grid_config: Optional[GridConfig] = None
    store_position: Positioni
    customer_position: Positioni
    algorithm: SearchAlgorithm = SearchAlgorithm.ASTAR1
    heuristic: Heuristic = Heuristic.MANHATTAN
    animate: bool = False

class SearchResponse(BaseModel):
    success: bool
    path: Optional[List[str]] = None
    positions: Optional[List[Positioni]] = None
    total_cost: float = 0.0
    nodes_expanded: int = 0
    execution_time_ms: float = 0.0
    grid_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class PerformanceMetrics(BaseModel):
    algorithm: SearchAlgorithm
    heuristic: Heuristic
    nodes_expanded: int
    execution_time_ms: float
    path_cost: float
    path_length: int
    memory_peak_mb: float

class AssignmentRequest(BaseModel):
    grid_id: str
    assignment_strategy: str = "balanced"  # "pure_cost", "balanced", "hybrid"
    max_load_diff: int = 2

class AssignmentResponse(BaseModel):
    success: bool
    assignments: Dict[str, List[int]]  # store_id -> [customer_ids]
    total_cost: float
    store_loads: Dict[str, int]
    metrics: Dict[str, Any]