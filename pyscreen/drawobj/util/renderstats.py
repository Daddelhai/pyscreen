def blit_text(surface, text, pos, font):
    lines = text.splitlines() 
    space = font.size(' ')[0]
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in lines:
        line_surface = font.render(line, 1, (255,255,255), (0,0,0))
        _, line_height = line_surface.get_size()
        y += line_height  
        surface.blit(line_surface, (x, y))

def render_stats(surface, pos, font, obj, tabs = 0):
    text = ""
    for name, data in obj.render_stats.items():
        line = "    "*tabs
        if isinstance(data['time'],(int,float)):
            line += f"{name}: {int(data['time']*1_000_000)}us"
        else:
            line += f"{name}: {data['time'].microseconds}us"
        text += line + "\n"
        if hasattr(data["obj"], "render_stats"):
            text += render_stats(surface, pos, font, data["obj"], tabs+1 )
    if tabs == 0:
        blit_text(surface, text, pos, font)
    else:
        return text