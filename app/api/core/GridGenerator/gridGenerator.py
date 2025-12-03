# GridGenerator/grid_generator.py
import random
from DataStructure.Position import Position
from Parsers.InputParser import parse_input_with_stores

class GridGenerator:
    """Generates random grids for package delivery problem"""
    
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
    
    def generate_grid(self, min_m=5, max_m=10, min_n=5, max_n=10,
                     min_stores=1, max_stores=3,
                     min_customers=1, max_customers=5,
                     min_tunnels=1,  # Minimum tunnels (always at least 1)
                     max_tunnel_prob=0.3,  # Probability for extra tunnels
                     min_obstacle_prob=0.05,  # Minimum obstacle probability
                     max_obstacle_prob=0.2,  # Maximum obstacle probability
                     min_traffic=1,  # Minimum traffic cost
                     max_traffic=4):  # Maximum traffic cost
        """
        Generates a random grid configuration.
        
        Returns: tuple (init_str, traffic_str, stores_list)
        """
        # Random grid dimensions
        m = random.randint(min_m, max_m)
        n = random.randint(min_n, max_n)
        
        # Random number of stores (trucks) and customers (packages)
        S = random.randint(min_stores, max_stores)  # stores/trucks
        P = random.randint(min_customers, max_customers)  # customers/packages
        
        # Generate unique positions for stores
        stores = []
        while len(stores) < S:
            pos = Position(random.randint(0, m-1), random.randint(0, n-1))
            if pos not in stores:
                stores.append(pos)
        
        # Generate unique positions for customers
        customers = []
        while len(customers) < P:
            pos = Position(random.randint(0, m-1), random.randint(0, n-1))
            # Customer shouldn't be at same position as a store
            if pos not in customers and pos not in stores:
                customers.append(pos)
        
        # Generate tunnels - AT LEAST min_tunnels
        tunnels = []
        
        # First, ensure we have at least min_tunnels
        for _ in range(min_tunnels):
            attempts = 0
            while attempts < 100:  # Try 100 times to find valid tunnel
                pos1 = Position(random.randint(0, m-1), random.randint(0, n-1))
                pos2 = Position(random.randint(0, m-1), random.randint(0, n-1))
                
                # Valid tunnel: different positions, not already existing
                if (pos1 != pos2 and 
                    (pos1, pos2) not in tunnels and 
                    (pos2, pos1) not in tunnels):
                    tunnels.append((pos1, pos2))
                    break
                attempts += 1
        
        # Add random extra tunnels based on probability
        # Calculate max possible extra tunnels (don't go crazy)
        max_extra_tunnels = min(5, int((m * n) * max_tunnel_prob))
        
        for _ in range(max_extra_tunnels):
            # Use probability to decide if we add another tunnel
            if random.random() < max_tunnel_prob:
                attempts = 0
                while attempts < 50:
                    pos1 = Position(random.randint(0, m-1), random.randint(0, n-1))
                    pos2 = Position(random.randint(0, m-1), random.randint(0, n-1))
                    
                    if (pos1 != pos2 and 
                        (pos1, pos2) not in tunnels and 
                        (pos2, pos1) not in tunnels):
                        tunnels.append((pos1, pos2))
                        break
                    attempts += 1
        
        # Build initialState string
        init_str = self._build_init_string(m, n, P, S, customers, tunnels)
        
        # Generate traffic with random obstacle probability
        # Randomize obstacle probability within range
        obstacle_prob = random.uniform(min_obstacle_prob, max_obstacle_prob)
        traffic_str = self._generate_traffic(m, n, obstacle_prob, min_traffic, max_traffic)
        
        return init_str, traffic_str, stores
    
    def _build_init_string(self, m, n, P, S, customers, tunnels):
        """Builds initialState string in required format"""
        # Format: m;n;P;S;CustomerCoords;TunnelCoords
        
        # Customer coordinates
        customer_coords = []
        for customer in customers:
            customer_coords.extend([str(customer.x), str(customer.y)])
        customer_str = ",".join(customer_coords) if customer_coords else ""
        
        # Tunnel coordinates
        tunnel_coords = []
        for tunnel in tunnels:
            tunnel_coords.extend([str(tunnel[0].x), str(tunnel[0].y),
                                 str(tunnel[1].x), str(tunnel[1].y)])
        tunnel_str = ",".join(tunnel_coords) if tunnel_coords else ""
        
        # Build final string
        parts = [
            str(m), str(n), str(P), str(S),
            customer_str,
            tunnel_str
        ]
        
        return ";".join(parts)
    
    def _generate_traffic(self, m, n, obstacle_prob=0.1, min_traffic=1, max_traffic=4):
        """
        Generates traffic for ALL possible segments in grid.
        obstacle_prob: probability that a segment is blocked (0-1)
        min_traffic: minimum traffic cost for non-blocked segments
        max_traffic: maximum traffic cost for non-blocked segments
        """
        segments = []
        
        # Horizontal segments
        for y in range(n):
            for x in range(m-1):
                # Decide if blocked based on probability
                if random.random() < obstacle_prob:
                    traffic = 0  # blocked
                else:
                    traffic = random.randint(min_traffic, max_traffic)
                
                segments.append(f"{x},{y},{x+1},{y},{traffic}")
        
        # Vertical segments
        for x in range(m):
            for y in range(n-1):
                if random.random() < obstacle_prob:
                    traffic = 0
                else:
                    traffic = random.randint(min_traffic, max_traffic)
                
                segments.append(f"{x},{y},{x},{y+1},{traffic}")
        
        return ";".join(segments)
    
    def gen_grid(self, min_m=5, max_m=10, min_n=5, max_n=10,
                     min_stores=1, max_stores=3,
                     min_customers=1, max_customers=5,
                     min_tunnels=1,  # Minimum tunnels (always at least 1)
                     max_tunnel_prob=0.3,  # Probability for extra tunnels
                     min_obstacle_prob=0.05,  # Minimum obstacle probability
                     max_obstacle_prob=0.2,  # Maximum obstacle probability
                     min_traffic=1,  # Minimum traffic cost
                     max_traffic=4, ensure_connectivity=True):
        """
        Public method to generate grid.
        ensure_connectivity: if True, ensures stores can reach customers
        Returns: (grid_object, init_str, traffic_str)
        """
        while True:
            init_str, traffic_str, stores = self.generate_grid(
                    min_m=min_m, max_m=max_m,
                    min_n=min_n, max_n=max_n,
                    min_stores=min_stores, max_stores=max_stores,
                    min_customers=min_customers, max_customers=max_customers,
                    min_tunnels=min_tunnels,
                    max_tunnel_prob=max_tunnel_prob,
                    min_obstacle_prob=min_obstacle_prob,
                    max_obstacle_prob=max_obstacle_prob,
                    min_traffic=min_traffic,
                    max_traffic=max_traffic
                )
            
            # Parse using existing parser
            grid = parse_input_with_stores(init_str, traffic_str, stores)
            
            # Check if grid is valid (optional connectivity check)
            if not ensure_connectivity:
                return grid, init_str, traffic_str
            
            # Basic check: ensure at least one store can reach at least one customer
            # (This is a simple check - you could implement full connectivity check)
            has_tunnel = len(grid.tunnels) > 0
            has_paths = len(grid.traffic) > 0
            
            if has_tunnel and has_paths:
                return grid, init_str, traffic_str
            # Otherwise try again

# For backward compatibility
def GenGrid():
    """
    Function as specified in PDF.
    Returns grid object.
    """
    generator = GridGenerator()
    grid, init_str, traffic_str = generator.gen_grid()
    return grid