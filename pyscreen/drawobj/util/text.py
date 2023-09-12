from pygame import Surface
from pygame.font import Font

class _line:
    def __init__(self, line: str):
        self.line: str = line

    def words(self):
        return self.line.split(' ')

    def render(self, font: Font, color: tuple, background: tuple|None = None, antialias:bool = True, width: int|None = None, surface_flags:int = 0):
        if width is None:
            return font.render(self.line, antialias, color, background)

        surfaces = []
        x = 0
        y = 0
        h = 0
        gap = font.size(' ')[0]

        for word in self.words():
            s = font.render(word, antialias, color, background)
            size_x, size_y = s.get_size()

            if x + size_x > width:
                x = 0
                y = h

            h = max(y + size_y, h)

            surfaces.append({
                'x': x,
                'y': y,
                'surface': s
            })
            x = x + size_x + gap

        surf = Surface((width,h),surface_flags)
        for s in surfaces:
            surf.blit(s['surface'], (s['x'], s['y']))

        return surf



def text(text: str, font: Font, color: tuple, background: tuple|None=None, width=None, antialias:bool = True, surface_flags:int=0, nl_gap:int=0):
    lines = [_line(l) for l in text.splitlines()] 

    surfaces = []
    y = 0

    mw = 0
    for line in lines:
        s = line.render(font, color, background, antialias, width, surface_flags)
        w, size_y = s.get_size()
        if w > mw:
            mw = w
        surfaces.append({
            'x': 0,
            'y': y,
            'surface': s
        })
        y += size_y + nl_gap

    surf = Surface((width if width is not None else mw,y), surface_flags)
    for s in surfaces:
        surf.blit(s['surface'], (s['x'], s['y']))
    
    return surf