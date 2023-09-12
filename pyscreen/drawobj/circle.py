from typing import overload

from pygame import draw
from pygame.draw import circle as pygame_circle
from pygame.draw import ellipse

from pyscreen.core.vector import Vector2, IntVector2, IVector2


@overload
def circle(surface, color, pos1: Vector2, pos2: Vector2, width: int=0):
    ...
@overload
def circle(surface, color, center: Vector2, radius: float, width: int=0):
    ...
@overload
def circle(surface, color, center, radius: float, width: int=0):
    ...


def circle(*args):
    if isinstance(args[2], (IntVector2, Vector2)):
        if isinstance(args[3], (IntVector2, Vector2)):
            return _circle_pos(*args)
        return _circle_rad1(*args)
    else:
        return _circle_rad2(*args)

def _circle_pos(surface, color, pos1: IVector2, pos2: IVector2, width: int=0):
    pos1 = pos1.asInts()
    pos2 = pos2.asInts()

    x_min = min(pos1.x, pos2.x)
    x_max = max(pos1.x, pos2.x)
    y_min = min(pos1.y, pos2.y)
    y_max = max(pos1.y, pos2.y)

    size_x = x_max - x_min
    size_y = y_max - y_min

    ellipse(surface, color, (x_min, y_min, size_x, size_y), width)

def _circle_rad1(surface, color, center: IVector2, radius: float|int, width: int=0):
    center = center.asInts()
    pygame_circle(surface, color, (center.x, center.y), radius, width)

def _circle_rad2(surface, color, center, radius: float, width: int=0):
    pygame_circle(surface, color, center, radius, width)