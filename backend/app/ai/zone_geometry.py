from typing import List, Tuple

def get_bottom_center_point(bbox: Tuple[int, int, int, int]) -> Tuple[float, float]:
    """
    Computes the bottom-center point (foot position) of a 2D bounding box (x1, y1, x2, y2).
    This ground contact point is used for accurate restricted zone spatial boundary checks.
    
    Args:
        bbox: Bounding box tuple (x1, y1, x2, y2)
        
    Returns:
        Tuple[float, float]: (bottom_center_x, bottom_center_y)
    """
    x1, y1, x2, y2 = bbox
    bottom_center_x = (x1 + x2) / 2.0
    bottom_center_y = float(y2)
    return (bottom_center_x, bottom_center_y)

def is_point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Ray-casting algorithm to determine if a point (x, y) lies inside a 2D polygon defined by vertices.
    
    Args:
        point: (x, y) coordinates of the detection position.
        polygon: List of (x, y) tuple vertices defining the restricted hazardous boundary.
        
    Returns:
        bool: True if point is inside polygon, False otherwise.
    """
    x, y = point
    inside = False
    n = len(polygon)
    if n < 3:
        return False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def is_person_in_restricted_zone(bbox: Tuple[int, int, int, int], polygon: List[Tuple[float, float]]) -> bool:
    """
    Performs point-in-polygon check using the person's bottom-center point.
    
    Args:
        bbox: Bounding box tuple (x1, y1, x2, y2)
        polygon: Restricted zone polygon coordinates
        
    Returns:
        bool: True if person's bottom-center is inside restricted zone, False otherwise.
    """
    bottom_center = get_bottom_center_point(bbox)
    return is_point_in_polygon(bottom_center, polygon)
