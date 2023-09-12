from typing import overload
import numpy as np
from pygame.draw import arc as pygame_arc
from pygame import Surface, SRCALPHA
from pygame.transform import scale

from pyscreen.core.vector import Vector2, IntVector2, IVector2
from pyscreen.core.angle import Angle

from pyscreen.settings import AASUPERSAMPLING

PI = np.pi

@overload
def arc(surface: Surface, color, pos1: IVector2, pos2: IVector2, start_angle: Angle, stop_angle: Angle, width: int=1): ...
@overload
def arc(surface: Surface, color, center: IVector2, radius: int, start_angle: Angle, stop_angle: Angle, width: int=1): ...


def arc(surface: Surface, color, a: IVector2, b: IVector2|int, start_angle: Angle, stop_angle: Angle, width: int=1):
    if isinstance(b, int):
        return _arc2(surface, color, a, b, start_angle, stop_angle, width)
    else:
        return _arc1(surface, color, a, b, start_angle, stop_angle, width)

def _arc1(surface: Surface, color, pos1: IVector2, pos2: IVector2, start_angle: Angle, stop_angle: Angle, width: int=1):
    if isinstance(pos1, Vector2):
        pos1 = pos1.asInts()
    if isinstance(pos2, Vector2):
        pos2 = pos2.asInts()

    x_min = min(pos1.x, pos2.x)
    x_max = max(pos1.x, pos2.x)
    y_min = min(pos1.y, pos2.y)
    y_max = max(pos1.y, pos2.y)

    size_x = x_max - x_min
    size_y = y_max - y_min

    pygame_start_angle = -stop_angle.rad + PI / 2
    pygame_stop_angle = -start_angle.rad + PI / 2
    
    pygame_arc(surface, color, (x_min,y_min,size_x,size_y), pygame_start_angle, pygame_stop_angle, width)

def _arc2(surface: Surface, color, center: IVector2, radius: int, start_angle: Angle, stop_angle: Angle, width: int=1):
    pos1 = IntVector2(center[0] - radius, center[1] - radius)
    pos2 = IntVector2(center[0] + radius, center[1] + radius)

    _arc1(surface, color, pos1, pos2, start_angle, stop_angle, width)



@overload
def aaarc(surface: Surface, color, pos1: IVector2, pos2: IVector2, start_angle: Angle, stop_angle: Angle, width: int=1): ...
@overload
def aaarc(surface: Surface, color, center: IVector2, radius: int, start_angle: Angle, stop_angle: Angle, width: int=1): ...


def aaarc(surface: Surface, color, a: IVector2, b: IVector2|int, start_angle: Angle, stop_angle: Angle, width: int=1):
    if isinstance(b, int):
        return _aaarc2(surface, color, a, b, start_angle, stop_angle, width)
    else:
        return _aaarc1(surface, color, a, b, start_angle, stop_angle, width)


def _aaarc1(surface: Surface, color, pos1: IVector2, pos2: IVector2, start_angle: Angle, stop_angle: Angle, width: int=1):
    if isinstance(pos1, Vector2):
        pos1 = pos1.asInts()
    if isinstance(pos2, Vector2):
        pos2 = pos2.asInts()

    size_x, size_y = pos1 - pos2
    size_orig = IntVector2(abs(size_x), abs(size_y))
    size = size_orig * AASUPERSAMPLING

    tmp_surface: Surface = Surface(tuple(size_orig.asInts()), SRCALPHA, 32)
    super_surface: Surface = Surface(tuple(size.asInts()), SRCALPHA, 32)

    if len(color) == 4:
        c = (color[0], color[1], color[2], int(color[3]*0.25))
    else:
        c = (color[0], color[1], color[2], 64)

    _arc1(tmp_surface, c, IntVector2(0,0), size_orig , start_angle, stop_angle, width)
    _arc1(super_surface, color, IntVector2(0,0), size , start_angle, stop_angle, width * AASUPERSAMPLING)

    aa_surface = scale(super_surface, (size_orig.x, size_orig.y))
    tmp_surface.blit(aa_surface, (0,0))
    surface.blit(tmp_surface, (pos1[0],pos1[1]))

def _aaarc2(surface: Surface, color, center: IVector2, radius: int, start_angle: Angle, stop_angle: Angle, width: int=1):
    pos1 = IntVector2(center[0] - radius, center[1] - radius)
    pos2 = IntVector2(center[0] + radius, center[1] + radius)

    _aaarc1(surface, color, pos1, pos2, start_angle, stop_angle, width)