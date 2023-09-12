from pygame import SRCALPHA, Surface
from pygame.font import Font

import pyscreen.drawobj.draw as draw
from pyscreen.core.vector import Vector2
from pyscreen.eventHandler import EventHandler
from pyscreen.hitbox import Hitbox
from pyscreen.drawobj.elements._util.padding import get_innerheight, get_innerwidth, get_outerheight, get_outerwidth, get_padding

from ..base import ElementWithHitbox


class DropDownBox(ElementWithHitbox):
    def __init__(self, eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, value="", padding=(2,8,2,8), margin=(0,0,0,0)):
        super().__init__(eventHandler, padding, margin, width, height)
        self._font = font
        self.location = Vector2(location)
        self._background = background
        self._color = color
        self._border = border_color
        self._value = value
        self.absolute_offset = Vector2(0,0)

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
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        self._changed = True


    async def releaseFocus(self):
        if self.hitbox is not None:
            await self.hitbox.releaseFocus()

    def _calc_height(self):
        text_surface = self.font.render(" ", False, (0,0,0))
        x,y = text_surface.get_size()
        return y+self.padding.top+self.padding.bottom

    async def focus(self, e):
        if not self.hitbox.hasFocus:
            await self.hitbox.manual_focus(lambda: self.value)
        
    @property
    def innerwidth(self):
        if self._width is None:
            return self._calc_innerwidth()
        return get_innerwidth(self._width, self.padding)

    @property
    def width(self):
        if self._width is None:
            return get_outerwidth(self._calc_innerwidth(), self.padding)
        return self._width

    @width.setter
    def width(self, value):
        if value is None:
            self._width = None
            return
        if value < 0:
            raise ValueError("height cannot be negative")
        self._width = value
        self._changed = True

    @property
    def innerheight(self):
        return self._calc_innerheight()

    @property
    def height(self):
        return get_outerheight(self._calc_innerheight(), self.padding)

    @height.setter
    def height(self, value):
        raise NotImplementedError("Cannot set height of a dropdown box. Use padding and font size instead")

    def addEventListener(self, *args, **kwargs):
        self.hitbox.addEventListener(*args, **kwargs)

    def render(self, surface: Surface|None=None):
        if not self.visible:
            return
            
        show_value = self.value

        # Text

        text_surface = self.font.render(show_value, True, self.color, self.background)
        frame_surface = Surface(
            (self.width, self.height), SRCALPHA, 32
        )

        if self.background is not None:
            frame_surface.fill(self.background)


        dx,dy = (self.padding.left,self.padding.top)

        frame_surface.blit(text_surface, (dx,dy),(0,0,self.width-2*self.padding.right-self.padding.left,self.innerheight))

        if self.border is not None:
            sx, sy = frame_surface.get_size()
            draw.rectangle(frame_surface,self.border,(0,0),(sx,sy),1)
        # Symbol

        symbol_surface = Surface(
            (self.innerheight, self.innerheight), SRCALPHA, 32
        )
        if not self.hitbox.hasFocus:
            draw.aapolygon(symbol_surface,self.color,[
                (self.innerheight // 4,self.innerheight // 4),
                (self.innerheight - self.innerheight // 4,self.innerheight // 4),
                (self.innerheight//2,self.innerheight - self.innerheight // 4)
            ])
        else:
            draw.aapolygon(symbol_surface,self.color,[
                (self.innerheight // 4,self.innerheight - self.innerheight // 4),
                (self.innerheight - self.innerheight // 4,self.innerheight - self.innerheight // 4),
                (self.innerheight//2,self.innerheight // 4)
            ])

        frame_surface.blit(symbol_surface, (
            self.width - self.padding.right - self.innerheight,
            self.padding.top
        ))

        # Final
        if surface is not None:
            self.hitbox.hitbox_location: Vector2 = self.location
            surface.blit(frame_surface, tuple(self.location))

        self.hitbox.hitbox_size = Vector2(frame_surface.get_size())

        self._changed = False
        return frame_surface

    def setOffset(self, offset: Vector2):
        self.absolute_offset: Vector2 = offset
        self.hitbox.hitbox_location: Vector2 = self.absolute_offset

    def _calc_innerheight(self):
        h = self.font.get_height()
        return h + self.padding.top + self.padding.bottom

    def _calc_innerwidth(self):
        show_value = self.value
        if self.hitbox is None or self.hitbox.hasFocus:
            show_value += " "

        text_surface = self.font.render(show_value, False, (0,0,0))
        x,y = text_surface.get_size()
        return x