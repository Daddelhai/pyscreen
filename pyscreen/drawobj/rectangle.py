import pygame

from pyscreen.core.vector import IVector2, IntVector2


def rectangle(surface, color, pos1: IVector2, pos2: IVector2, width=0, border_radius=(-1,-1,-1,-1)):
    if not isinstance(pos1, IntVector2):
        pos1 = IntVector2(pos1)
    if not isinstance(pos2, IntVector2):
        pos2 = IntVector2(pos2)
        
    x_min = int(min(pos1.x, pos2.x))
    x_max = int(max(pos1.x, pos2.x))
    y_min = int(min(pos1.y, pos2.y))
    y_max = int(max(pos1.y, pos2.y))

    size_x = x_max - x_min
    size_y = y_max - y_min

    pygame.draw.rect(surface, color, (x_min, y_min, size_x, size_y), width,
        border_top_right_radius=border_radius[0],
        border_bottom_right_radius=border_radius[1],
        border_bottom_left_radius=border_radius[2],
        border_top_left_radius=border_radius[3],
    )