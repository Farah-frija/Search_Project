from DataStructure.Edge import Edge
from DataStructure.Position import Position


def parse_traffic_string(traffic_str):
    """
    Parses traffic string into list of edges with traffic levels.
    Format: "srcX1,srcY1,dstX1,dstY1,traffic1;srcX2,srcY2,dstX2,dstY2,traffic2;..."
    
    Returns: dictionary where key=Edge, value=traffic (int)
    """
    traffic_dict = {}
    
    if not traffic_str or traffic_str.strip() == "":
        return traffic_dict
    
    segments = traffic_str.strip().split(';')
    
    for seg in segments:
        if not seg:
            continue
            
        parts = seg.split(',')
        if len(parts) != 5:
            continue  # or raise error
            
        src_x, src_y, dst_x, dst_y, traffic = map(int, parts)
        
        src = Position(src_x, src_y)
        dst = Position(dst_x, dst_y)
        
        # Create edge (undirected)
        edge = Edge(src, dst)
        traffic_dict[edge] = traffic
        
        # Also add reverse direction for consistency
        # (though Edge.__eq__ handles both directions)
    
    return traffic_dict