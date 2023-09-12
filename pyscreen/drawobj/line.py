from pygame.draw import line as pygame_line

from pyscreen.core.vector import Vector2, IntVector2, IVector2


def line(surface, color, pos1: IVector2|tuple, pos2: IVector2|tuple, width:int = 1):
    pos1 = IntVector2(pos1)
    pos2 = IntVector2(pos2)

    surf_max_x, surf_max_y = surface.get_size()
    if pos1.x > surf_max_x and pos2.x > surf_max_x:
        return
    if pos1.y > surf_max_y and pos2.y > surf_max_y:
        return
    if pos1.x < 0 and pos2.x < 0:
        return
    if pos1.y < 0 and pos2.y < 0:
        return

    pygame_line(surface, color, (pos1.x, pos1.y), (pos2.x, pos2.y), width)

def dashed_line(surface, color, pos1: Vector2|tuple, pos2: Vector2|tuple, width:int=1, dash_length:int=10):
    pos1 = IntVector2(pos1)
    pos2 = IntVector2(pos2)

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
        line(surface, color, start, end, width)