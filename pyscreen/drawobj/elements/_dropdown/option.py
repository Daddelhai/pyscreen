from typing import Any
from pygame import Surface, SRCALPHA
import pyscreen.drawobj.draw as draw
from pygame.font import Font
from pyscreen.core.vector import Vector2
from pyscreen.drawobj.elements._util.padding import get_padding
from pyscreen.hitbox import Hitbox
from pyscreen.eventHandler import EventHandler
from ..button import Button, ElementWithHitbox

class DropDownOption(Button):
    def __init__(self, key:Any, value:str, eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, padding=(2,8,2,8), margin=(0,0,0,0), text_align=0):
        ElementWithHitbox.__init__(self, eventHandler, padding, margin, width, height)
        self._visible = True
        self.font = font
        self.location = Vector2(location)
        self.background = background
        self.color = color
        self.border = border_color
        self.value = value
        self.key = key
        self.offset = Vector2(0,0)
        self.text_align = text_align
        self.listeners = []

    def destruct(self):
        for l in self.listeners:
            if self.hitbox.removeEventListener(l) == 0:
                raise RuntimeError("Cannot remove click handler in _DropDownOption")      
        super().destruct()

    def addEventListener(self, *args, **kwargs):
        l = self.hitbox.addEventListener(*args, **kwargs)
        self.listeners.append(l)
        return l

    def render(self, surface):
        show_value = self.value

        text_surface = self.font.render(show_value, True, self.color, self.background)
        frame_surface = Surface(
            (self.width, self.height), SRCALPHA, 32
        )

        if self.background is not None:
            frame_surface.fill(self.background)

        if self.border is not None:
            sx, sy = frame_surface.get_size()
            draw.rectangle(frame_surface,self.border,(0,0),(sx,sy),1)

        tx,ty = text_surface.get_size()
        fx,fy = frame_surface.get_size()
        
        if self.text_align == -1:
            frame_surface.blit(text_surface, (self.padding.left,self.padding.top))
        elif self.text_align == 0:
            dx = (fx - (tx + self.padding.left + self.padding.right)) / 2
            frame_surface.blit(text_surface, (self.padding.left+dx,self.padding.top))
        elif self.text_align == 1:
            dx = (fx - (tx + self.padding.left + self.padding.right))
            frame_surface.blit(text_surface, (self.padding.left+dx,self.padding.top))

        surface.blit(frame_surface, tuple(self.location.asInts()))

        self.hitbox.hitbox_size = Vector2(frame_surface.get_size())
        self.hitbox.hitbox_location = self.location+self.offset