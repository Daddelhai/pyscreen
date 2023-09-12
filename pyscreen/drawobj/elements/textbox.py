from time import time

from pygame import K_BACKSPACE, K_RETURN, SRCALPHA, Surface
from pygame.font import Font

import pyscreen.drawobj.draw as draw
from pyscreen.core.vector import Vector2
from pyscreen.eventHandler import EventHandler

from .base import ElementWithHitbox


class Textbox(ElementWithHitbox):
    def __init__(self, eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, value="", max_length=None, padding=(2,8,2,8), margin=(2,8,2,8), placeholder:str=""):
        super().__init__(eventHandler, padding, margin, width, height)
        self._font = font
        self.location = Vector2(location)
        self._background = background
        self._color = color
        self._border = border_color
        self._value = value
        self.max_length = max_length
        self._placeholder = placeholder

        self.hitbox.addEventListener("mouseDown", self.focus)

        self.__override_event = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._changed = True
        if self.max_length is not None:
            value = value[:self.max_length]
        else:
            self._value = value

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
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        self._placeholder = value
        self._changed = True

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        self._changed = True

    async def _onKeydown(self, event):
        if event.key == K_BACKSPACE:
            self.value = self.value[:-1]
        elif event.key == K_RETURN:
            await self.hitbox.releaseFocus()
        elif self.max_length is None or len(self.value) < self.max_length:
            self.value = self.value + event.unicode

    async def focus(self, e):
        if not self.hitbox.hasFocus:
            await self.hitbox.focus(lambda: self.value)
            self.__override_event = self.hitbox.outer.addEventListener("keyDown", self._onKeydown, override=True)
            def leave(e):
                self.hitbox.removeEventListener(self.__override_event)
                self.__override_event = None
            self.hitbox.addEventListener("focusRelease", leave, True)

    @property
    def _show_value(self) -> str:
        return str(self.value)


    def render(self, surface: Surface|None = None):
        if not self.visible:
            return

        show_value = self._show_value
        if self.hitbox.hasFocus:
            if int(time()*2) & 1:
                show_value += "|"
            else:
                show_value += " "
        elif show_value == "":
            show_value = self._placeholder


        text_surface = draw.text(show_value, self._font, self._color, self._background)
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
        dx,dy = (self.padding.left,self.padding.top)

        if tx+self.padding.left+self.padding.right > fx:
            dx = fx - (tx+self.padding.left+self.padding.right) + self.padding.left
        if ty+self.padding.top+self.padding.bottom > fy:
            dy = fy - (ty+self.padding.top+self.padding.bottom) + self.padding.top

        frame_surface.blit(text_surface, (dx,dy))
        if surface is not None:
            surface.blit(frame_surface, tuple(self.location))

        self.hitbox.hitbox_size = Vector2(frame_surface.get_size())
        self._changed = False
        return frame_surface    

    def _calc_innerheight(self):
        return self._font.get_height()

    def _calc_innerwidth(self):
        show_value = self.value
        if self.hitbox is None or self.hitbox.hasFocus:
            show_value += " "

        text_surface = self._font.render(show_value, False, (0,0,0))
        x,y = text_surface.get_size()
        return x