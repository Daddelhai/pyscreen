from typing import overload

from pygame.draw import ellipse
from pygame.gfxdraw import aacircle as pygame_aacircle
from pygame.gfxdraw import aaellipse

from pyscreen.core.vector import Vector2, IVector2, IntVector2

from .circle import _circle_rad1, _circle_rad2


@overload
def aacircle(surface, color, pos1: IVector2, pos2: IVector2, fill: bool= False):
    ...
@overload
def aacircle(surface, color, center: IVector2, radius: float, width: int=0):
    ...
@overload
def aacircle(surface, color, center, radius: float, width: int=0):
    ...

def aacircle(*args):
    if isinstance(args[2], (IntVector2, Vector2)):
        if isinstance(args[3], (IntVector2, Vector2)):
            return _aacircle_pos(*args)
        return _aacircle_rad1(*args)
    else:
        return _aacircle_rad2(*args)

def _aacircle_pos(surface, color, pos1: IVector2, pos2: IVector2, fill: bool= False):
    pos1 = pos1.asInts()
    pos2 = pos2.asInts()

    x_min = min(pos1.x, pos2.x)
    x_max = max(pos1.x, pos2.x)
    y_min = min(pos1.y, pos2.y)
    y_max = max(pos1.y, pos2.y)

    size_x = x_max - x_min
    size_y = y_max - y_min

    aaellipse(surface, x_min, y_min, size_x, size_y, color)
    if fill:
        ellipse(surface, color, (x_min, y_min, size_x, size_y))

def _aacircle_rad1(surface, color, center: IVector2, radius, width: int= 0):
    center = center.asInts()

    if width <= 1:
        pygame_aacircle(surface, center.x, center.y, radius, color)
        if width == 0:
            _circle_rad1(surface, color, center, radius, 0)
    else:
        _aacircle_rad1(surface, color, center, radius + width/2, 1)
        _aacircle_rad1(surface, color, center, radius - width/2, 1)
        _circle_rad1(surface, color, center, radius, width)

def _aacircle_rad2(surface, color, center, radius, width: int= 0):
    if width <= 1:
        pygame_aacircle(surface, int(center[0]), int(center[1]), radius, color)
        if width == 0:
            _circle_rad2(surface, color, center, radius, 0)
    else:
        _aacircle_rad2(surface, color, center, radius + width/2, 1)
        _aacircle_rad2(surface, color, center, radius - width/2, 1)
        _circle_rad2(surface, color, center, radius, width)
        
