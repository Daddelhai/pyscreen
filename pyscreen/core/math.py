from functools import lru_cache

@lru_cache(maxsize=100)
def get_segment_segment_intersection(p0_x: float, p0_y: float, p1_x: float, p1_y: float, 
    p2_x: float, p2_y: float, p3_x: float, p3_y: float):

    
    s1_x: float = p1_x - p0_x
    s1_y: float = p1_y - p0_y
    s2_x: float = p3_x - p2_x   
    s2_y: float = p3_y - p2_y

    s: float = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y)
    t: float = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)

    if s >= 0 and s <= 1 and t >= 0 and t <= 1:
    
        i_x: float = p0_x + (t * s1_x)
        i_y: float = p0_y + (t * s1_y)

        return i_x, i_y

    return None

@lru_cache(maxsize=100)
def get_segment_ray_intersection(p0_x: float, p0_y: float, p1_x: float, p1_y: float, 
    p2_x: float, p2_y: float, p3_x: float, p3_y: float):

    
    s1_x: float = p1_x - p0_x
    s1_y: float = p1_y - p0_y
    s2_x: float = p3_x - p2_x   
    s2_y: float = p3_y - p2_y

    s: float = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y)
    t: float = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)

    if s >= 0 and t >= 0 and t <= 1:
    
        i_x: float = p0_x + (t * s1_x)
        i_y: float = p0_y + (t * s1_y)

        return i_x, i_y

    return None

@lru_cache(maxsize=100)
def get_line_ray_intersection(p0_x: float, p0_y: float, p1_x: float, p1_y: float, 
    p2_x: float, p2_y: float, p3_x: float, p3_y: float):

    
    s1_x: float = p1_x - p0_x
    s1_y: float = p1_y - p0_y
    s2_x: float = p3_x - p2_x   
    s2_y: float = p3_y - p2_y

    s: float = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y)
    t: float = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)

    if s >= 0:
    
        i_x: float = p0_x + (t * s1_x)
        i_y: float = p0_y + (t * s1_y)

        return i_x, i_y

    return None