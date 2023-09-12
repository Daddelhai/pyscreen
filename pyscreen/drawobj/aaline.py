from math import atan2, cos, sin

from pygame.draw import aaline as pygame_aaline

from pyscreen.core.vector import Vector2, IntVector2, IVector2

from .polygon import aapolygon, filled_polygon


def aaline(surface, color, pos1:IVector2, pos2:IVector2, width=1):
    if isinstance(pos1, Vector2):
        pos1 = pos1.asInts()
    if isinstance(pos2, Vector2):
        pos2 = pos2.asInts()

    surf_max_x, surf_max_y = surface.get_size()
    if pos1.x > surf_max_x and pos2.x > surf_max_x:
        return
    if pos1.y > surf_max_y and pos2.y > surf_max_y:
        return
    if pos1.x < 0 and pos2.x < 0:
        return
    if pos1.y < 0 and pos2.y < 0:
        return

    if width <= 1:
        pygame_aaline(surface, color, (pos1.x, pos1.y), (pos2.x, pos2.y) )
    
    else:
        center = (pos1 + pos2) / 2.
        length = (pos1 - pos2).length()
        angle = atan2(pos1.y - pos2.y, pos1.x - pos2.x)

        UL = (center.x + (length/2.) * cos(angle) - (width/2.) * sin(angle),
            center.y + (width/2.) * cos(angle) + (length/2.) * sin(angle))
        UR = (center.x - (length/2.) * cos(angle) - (width/2.) * sin(angle),
            center.y + (width/2.) * cos(angle) - (length/2.) * sin(angle))
        BL = (center.x + (length/2.) * cos(angle) + (width/2.) * sin(angle),
            center.y - (width/2.) * cos(angle) + (length/2.) * sin(angle))
        BR = (center.x - (length/2.) * cos(angle) + (width/2.) * sin(angle),
            center.y - (width/2.) * cos(angle) - (length/2.) * sin(angle))

        aapolygon(surface, color, (UL, UR, BR, BL))
        filled_polygon(surface, color, (UL, UR, BR, BL))

def dashed_aaline(surface, color, pos1:IVector2, pos2:IVector2, width=1, dash_length=10):
    if isinstance(pos1, Vector2):
        pos1 = pos1.asInts()
    if isinstance(pos2, Vector2):
        pos2 = pos2.asInts()

    surf_max_x, surf_max_y = surface.get_size()
    if pos1.x > surf_max_x and pos2.x > surf_max_x:
        return
    if pos1.y > surf_max_y and pos2.y > surf_max_y:
        return
    if pos1.x < 0 and pos2.x < 0:
        return
    if pos1.y < 0 and pos2.y < 0:
        return

    displacement = pos2 - pos1
    length = displacement.length()
    slope = displacement/length

    for index in range(0, int(length/dash_length), 2):
        start = pos1 + (slope *    index    * dash_length)
        end   = pos1 + (slope * (index + 1) * dash_length)
        aaline(surface, color, start, end, width)