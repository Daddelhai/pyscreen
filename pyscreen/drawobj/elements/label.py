from pygame import Surface, SRCALPHA
import pyscreen.drawobj.draw as draw
from pygame.font import Font
from pyscreen.core.vector import Vector2
from pyscreen.hitbox import Hitbox
from pyscreen.eventHandler import EventHandler
from .base import ElementWithHitbox

class Label(ElementWithHitbox):
    def __init__(self, value:str, eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, max_length=None, padding=(2,8,2,8), margin=(0,0,0,0), text_align=0):
        super().__init__(eventHandler, padding, margin, width, height)
        self._font = font
        self.location = Vector2(location)
        self._background = background
        self._color = color
        self._border = border_color
        self._value = value
        self.max_length = max_length
        self._text_align = text_align

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._changed = True

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        self._changed = True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._changed = True

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, value):
        self._border = value
        self._changed = True

    @property
    def text_align(self):
        return self._text_align

    @text_align.setter
    def text_align(self, value):
        self._text_align = value
        self._changed = True

    def render(self, surface: Surface|None=None):
        if not self.visible:
            return
        
        show_value = str(self._value)

        text_surface = self._font.render(show_value, True, self._color, self._background)
        frame_surface = Surface(
            (self.width, self.height), SRCALPHA, 32
        )

        if self._background is not None:
            frame_surface.fill(self._background)

        if self._border is not None:
            sx, sy = frame_surface.get_size()
            draw.rectangle(frame_surface,self._border,(0,0),(sx,sy),1)

        tx,ty = text_surface.get_size()
        fx,fy = frame_surface.get_size()
        
        vertical_align = 0
        if fy < ty - self.padding.top - self.padding.bottom:
            vertical_align = (fy - (ty + self.padding.top + self.padding.bottom)) // 2
        
        if self._text_align == -1:
            frame_surface.blit(text_surface, (self.padding.left, self.padding.top+vertical_align))
        elif self._text_align == 0:
            horizontal_align = (fx - (tx + self.padding.left + self.padding.right)) / 2
            frame_surface.blit(text_surface, (self.padding.left+horizontal_align, self.padding.top+vertical_align))
        elif self._text_align == 1:
            horizontal_align = (fx - (tx + self.padding.left + self.padding.right))
            frame_surface.blit(text_surface, (self.padding.left+horizontal_align, self.padding.top+vertical_align))

        if surface is not None:
            surface.blit(frame_surface, tuple(self.location))

        self.hitbox.hitbox_size = Vector2(frame_surface.get_size())

        self._changed = False
        return frame_surface


    def _calc_innerheight(self):
        return self._font.get_height()

    def _calc_innerwidth(self):
        show_value = str(self._value)
        if self.hitbox is None or self.hitbox.hasFocus:
            show_value += " "

        text_surface = self._font.render(show_value, False, (0,0,0))
        x,y = text_surface.get_size()
        return x
    
    def printHitbox(self, surface, color=(0,255,0)):
        super().printHitbox(surface, color)