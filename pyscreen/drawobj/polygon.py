from pygame.draw import polygon as pygame_polygon
from pygame.gfxdraw import aapolygon as pygame_aapolygon
from pygame.gfxdraw import filled_polygon as pygame_filled_polygon


def polygon(surface, color, pos, width):
    pygame_polygon(surface, color, pos, width)

def filled_polygon(surface, color, pos):
    pygame_filled_polygon(surface, pos, color)

def aapolygon(surface, color, pos):
    pygame_aapolygon(surface, pos, color)