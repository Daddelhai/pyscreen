from functools import lru_cache
import pygame
from pyscreen.core.entity import StaticEntity
from pyscreen.core.vector import Vector2, IVector2

def BackgroundRGB(r, g, b, a=255) -> tuple:
    return (r, g, b, a)

def BackgroundRGBA(r, g, b, a=255) -> tuple:
    return (r, g, b, a)

def BackgroundHex(hex: str, default_a=255) -> tuple:
    """ Convert hex color to RGB color. Hex color can be in format '#RRGGBB' or '#RRGGBBAA' """
    if len(hex) == 7:
        return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (default_a,)
    elif len(hex) == 9:
        return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4, 6))

def BackgroundHexA(hex: str, a=255) -> tuple:
    return BackgroundHex(hex, a)

def BackgroundHSV(h, s, v, a=255) -> tuple:
    # Transform HSV to RGB
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h >= 0 and h < 60:
        rgb = (c, x, 0)
    elif h >= 60 and h < 120:
        rgb = (x, c, 0)
    elif h >= 120 and h < 180:
        rgb = (0, c, x)
    elif h >= 180 and h < 240:
        rgb = (0, x, c)
    elif h >= 240 and h < 300:
        rgb = (x, 0, c)
    elif h >= 300 and h < 360:
        rgb = (c, 0, x)

    return tuple(int((i + m) * 255) for i in rgb) + (a,)

def BackgroundHSVA(h, s, v, a=255) -> tuple:
    return BackgroundHSV(h, s, v, a)

def BackgroundHSL(h, s, l, a=255) -> tuple:
    # Transform HSL to RGB
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if h >= 0 and h < 60:
        rgb = (c, x, 0)
    elif h >= 60 and h < 120:
        rgb = (x, c, 0)
    elif h >= 120 and h < 180:
        rgb = (0, c, x)
    elif h >= 180 and h < 240:
        rgb = (0, x, c)
    elif h >= 240 and h < 300:
        rgb = (x, 0, c)
    elif h >= 300 and h < 360:
        rgb = (c, 0, x)

    return tuple(int((i + m) * 255) for i in rgb) + (a,)

def BackgroundHSLA(h, s, l, a=255) -> tuple:
    return BackgroundHSL(h, s, l, a)

class BackgroundImage(StaticEntity):
    def __init__(self, path2image, size=None):
        self.image = pygame.image.load(path2image)
        if size is not None:
            if isinstance(size, IVector2):
                size = (size.x, size.y)
            self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()

    def render(self, surface: pygame.Surface|None = None):
        if surface is not None:
            surface.blit(self.image, self.rect)
        return self.image
    
    def render_scaled(self, size: tuple[int,int]|Vector2):
        if isinstance(size, IVector2):
            size = (size.x, size.y)
        return self._low_render_scaled(size)
    
    @lru_cache(maxsize=16)
    def _low_render_scaled(self, size: tuple[int,int]):
        image = pygame.transform.scale(self.image, size)
        return image

    @property
    def size(self):
        return self.rect.size
    
    @size.setter
    def size(self, size):
        if isinstance(size, IVector2):
            size = (size.x, size.y)
            
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()

    def get_size(self) -> tuple[int,int]:
        return self.size
    
    def get_position(self) -> tuple[int,int]:
        return self.rect.topleft
    
    def get_rect(self) -> pygame.Rect:
        return self.rect