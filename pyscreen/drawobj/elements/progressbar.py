from pygame import Surface, SRCALPHA
import pyscreen.drawobj.draw as draw
from pygame.font import Font
from pyscreen.core.vector import Vector2
from pyscreen.hitbox import Hitbox
from pyscreen.eventHandler import EventHandler
from .base import ElementWithHitbox

class Progressbar(ElementWithHitbox):
    def __init__(self, eventHandler: EventHandler, value:float = 0, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, border_radius=None, padding=(2,8,2,8), margin=(0,0,0,0), text_align=0):
        super().__init__(eventHandler, padding, margin, width, height)

        self.location = Vector2(location)
        self._background = background
        self._color = color
        self._border_color = border_color
        self._border_radius = border_radius
        self._value = value
        self._text_align = text_align

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value >= 0 and value <= 1:
            self._value = value
            self._changed = True
            return
        raise ValueError("Value must be between 0 and 1")

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
        return self._border_color

    @border.setter
    def border(self, value):
        self._border_color = value
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
        
        if self.width <= 0 or self.height <= 0:
            return

        frame_surface = Surface(
            (self.width, self.height), SRCALPHA, 32
        )

        fx,fy = frame_surface.get_size()
        left_x = self.padding.left
        top_y = self.padding.top
        right_x = fx - self.padding.right
        bottom_y = fy - self.padding.bottom
        available_width = fx - self.padding.left - self.padding.right

        if isinstance(self._border_radius, tuple):
            br = self._border_radius
        elif self._border_radius is not None:
            br = (self._border_radius,self._border_radius,self._border_radius,self._border_radius)
        else:
            br = (-1,-1,-1,-1)

        # draw background
        if self._background is not None:
            draw.rectangle(frame_surface,self._background,(left_x,top_y),(right_x,bottom_y),0,br)

        # draw progress
        prog_width = int(available_width * self._value)
        if prog_width > 0:
            draw.rectangle(frame_surface,self._color,(left_x,top_y),(left_x+prog_width,bottom_y),0,br)
        
        # draw border
        if self._border_color is not None:
            draw.rectangle(frame_surface,self._border_color,(left_x,top_y),(right_x,bottom_y),1,br) 


        if surface is not None:
            surface.blit(frame_surface, tuple(self.location))

        self.hitbox.hitbox_size = Vector2(frame_surface.get_size())

        self._changed = False
        return frame_surface


    def _calc_innerheight(self):
        return 0

    def _calc_innerwidth(self):
        return 0