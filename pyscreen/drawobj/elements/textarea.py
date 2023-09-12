import copy
from time import time

from pygame import K_BACKSPACE, K_RETURN, SRCALPHA, Surface
from pygame.font import Font

import pyscreen.drawobj.draw as draw
from pyscreen.core.vector import Vector2
from pyscreen.eventHandler import EventHandler
from pyscreen.hitbox import Hitbox
from pyscreen.drawobj.elements._util.padding import get_innerheight, get_innerwidth, get_outerheight, get_outerwidth, get_padding

from .base import ElementWithHitbox
from ._scrollbar.proxy import ScrollProxy


class Textarea(ElementWithHitbox):
    def __init__(self, eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, value="", max_length=None, padding=(2,8,2,8), margin=(0,0,0,0), readonly=False):
        super().__init__(eventHandler, padding, margin, width, height)
        self._font = font
        self.scrollProxy = ScrollProxy(eventHandler, max_height=height)
        self.location = Vector2(location)
        self._background = background
        self._color = color
        self._border = border_color
        self._value = value
        self.max_length = max_length

        if not readonly:
            self.hitbox.addEventListener("mouseClick", self.focus)

        self.__override_event = None

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

    @property
    def changed(self):
        return self._changed or self.hitbox.hasFocus

    async def _onKeydown(self, event):
        self._changed = True
        if event.key == K_BACKSPACE:
            self._value = self._value[:-1]
        elif event.key == K_RETURN:
            if self.eventHandler.shift_active:
                await self.hitbox.releaseFocus()
            else:
                self._value = self._value + "\n"
        elif self.max_length is None or len(self._value) < self.max_length:
            self._value = self._value + event.unicode

        self.scrollProxy.scroll_offset = copy.deepcopy(self.scrollProxy.scroll_maxoffset)

    async def focus(self, e):
        if not self.hitbox.hasFocus:
            await self.hitbox.focus(lambda: self._value)
            self.__override_event = self.hitbox.outer.addEventListener("keyDown", self._onKeydown, override=True)
            def leave(e):
                self.hitbox.removeEventListener(self.__override_event)
                self.__override_event = None
            self.hitbox.addEventListener("focusRelease", leave, True)
        

    def addEventListener(self, *args, **kwargs):
        self.hitbox.addEventListener(*args, **kwargs)


    def render(self, surface: Surface|None = None):
        if not self.visible:
            return

        show_value = self._value
        if self.hitbox.hasFocus:
            if int(time()*2) & 1:
                show_value += "|"
            else:
                show_value += " "


        mwidth = self.width - self.padding.left - self.padding.right
        text_surface = draw.text(show_value, self._font, self._color, self._background, mwidth)
        tx,ty = text_surface.get_size()

        fx = tx + self.padding.left + self.padding.right
        fy = ty + self.padding.top + self.padding.bottom

        frame_surface = Surface(
            (fx, fy), SRCALPHA, 32
        )

        if self._background is not None:
            frame_surface.fill(self._background)

        if self._border is not None:
            sx, sy = frame_surface.get_size()
            draw.rectangle(frame_surface,self._border,(0,0),(sx,sy),1)

        
        
        dx,dy = (self.padding.left,self.padding.top)

        if tx+self.padding.left+self.padding.right > fx:
            dx = fx - (tx+self.padding.left+self.padding.right) + self.padding.left
        if ty+self.padding.top+self.padding.bottom > fy:
            dy = fy - (ty+self.padding.top+self.padding.bottom) + self.padding.top

        frame_surface.blit(text_surface, (dx,dy))

        if self._height is not None:
            self.hitbox.hitbox_size = Vector2(fx,self._height)
            s = self.scrollProxy.render(frame_surface, self.hitbox.hitbox_location)
            if surface is not None:
                surface.blit(s, tuple(self.location))
            
            self._changed = False
            return s

        else:
            self.hitbox.hitbox_size = Vector2(fx,fy)
            if surface is not None:
                surface.blit(frame_surface, tuple(self.location))
            
            self._changed = False
            return frame_surface


    def _calc_innerheight(self):
        char_height = self._font.get_height()
        return char_height * len(self._value.splitlines())

    def _calc_innerwidth(self):
        show_value = self._value
        if self.hitbox is None or self.hitbox.hasFocus:
            show_value += " "

        x,y = self._font.size(show_value)
        return x