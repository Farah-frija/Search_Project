from DataStructure.Position import Position


def parse_initial_state(init_str):
    """
    Parses initialState string.
    Format: m;n;P;S;CustomerCoords;TunnelCoords
    
    Returns: dictionary with parsed values
    """
    parts = init_str.strip().split(';')
    
    if len(parts) < 4:
        raise ValueError("Invalid initialState format")
    
    m = int(parts[0])
    n = int(parts[1])
    P = int(parts[2])  # number of packages/customers
    S = int(parts[3])  # number of stores/trucks
    
    result = {
        'm': m, 'n': n, 'P': P, 'S': S,
        'customers': [],
        'tunnels': []
    }
    
    # Parse customer coordinates
    if len(parts) > 4:
        customer_str = parts[4]
        if customer_str:
            coords = list(map(int, customer_str.split(',')))
            if len(coords) % 2 != 0:
                raise ValueError("Customer coordinates must be in pairs")
            
            for i in range(0, len(coords), 2):
                x, y = coords[i], coords[i+1]
                result['customers'].append(Position(x, y))
    
    # Parse tunnel coordinates
    if len(parts) > 5:
        tunnel_str = parts[5]
        if tunnel_str:
            coords = list(map(int, tunnel_str.split(',')))
            if len(coords) % 4 != 0:  # Each tunnel needs 4 coordinates: x1,y1,x2,y2
                raise ValueError("Tunnel coordinates must be in groups of 4")
            
            for i in range(0, len(coords), 4):
                x1, y1, x2, y2 = coords[i], coords[i+1], coords[i+2], coords[i+3]
                result['tunnels'].append((Position(x1, y1), Position(x2, y2)))
    
    return result