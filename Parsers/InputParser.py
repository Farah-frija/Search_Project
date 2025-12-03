from DataStructure.Grid import Grid
from Parsers.InitialStateParser import parse_initial_state
from Parsers.TrafficParser import parse_traffic_string
def parse_input_with_stores(init_str, traffic_str, stores):
    """
    Parser that uses provided store locations.
    Use this when stores are known (e.g., from GridGenerator).
    """
    init_data = parse_initial_state(init_str)
    traffic_dict = parse_traffic_string(traffic_str)
    
    grid = Grid(init_data['m'], init_data['n'])
    
    # Add stores (provided)
    for store_pos in stores:
        grid.add_store(store_pos)
    
    # Add customers (from init_str)
    for customer_pos in init_data['customers']:
        grid.add_customer(customer_pos)
    
    # Add tunnels (from init_str)
    for entrance1, entrance2 in init_data['tunnels']:
        grid.add_tunnel(entrance1, entrance2)
    
    # Add traffic (from traffic_str)
    for edge, traffic_level in traffic_dict.items():
        grid.set_traffic(edge.pos1, edge.pos2, traffic_level)
    
    return grid

def parse_input(init_str, traffic_str):
    """
    Main parser: combines initialState and traffic parsing.
    Returns a Grid object fully initialized.
    """
    # Parse initialState
    init_data = parse_initial_state(init_str)
    
    # Parse traffic
    traffic_dict = parse_traffic_string(traffic_str)
    
    # Create Grid
    grid = Grid(init_data['m'], init_data['n'])
    
    # Add customers
    for customer_pos in init_data['customers']:
        grid.add_customer(customer_pos)
    
    # Add tunnels
    for entrance1, entrance2 in init_data['tunnels']:
        grid.add_tunnel(entrance1, entrance2)
    
    # Add traffic data
    for edge, traffic_level in traffic_dict.items():
        grid.set_traffic(edge.pos1, edge.pos2, traffic_level)
    
    # Note: Stores are NOT in initialState! 
    # We need to generate them or get them elsewhere.
    # For now, we'll assume stores are at fixed positions or generated separately.
    
    return grid

    