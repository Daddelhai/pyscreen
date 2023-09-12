from pygame.gfxdraw import pixel as pygame_pixel


def pixel(surface, color, pos):
    pygame_pixel(surface, pos[0], pos[1], color)