import inspect
from typing import Any
from pygame import Surface, SRCALPHA
import pyscreen.drawobj.draw as draw
from pygame.font import Font
from pyscreen.core.vector import Vector2
from pyscreen.eventHandler import EventHandler
from .base import Element
from .button import Button
from pyscreen.drawobj.elements._util.padding import get_outerheight, get_outerwidth, get_padding
from threading import RLock

class MultitoggleButton(Button):
    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key

class Multitoggle(Element):
    def __init__(self, values:dict[Any, str]|list[str], eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, background_active=None, color=(255,255,255), 
                 border=None, padding=(2,8,2,8), btn_padding=(2,8,2,8), text_align=0, gap=0, selected_index=None):
        super().__init__(eventHandler, padding, width, height)
        self._btn_padding = btn_padding
        self._font = font
        self.location = Vector2(location)
        self._background = background
        self._background_active = background_active
        self._color = color
        self._border = border
        self._values = values if isinstance(values, dict) else {v: v for v in values}
        self.selected_index = selected_index
        self._gap = gap
        self.absolute_offset = Vector2(0,0)
        self._text_align = text_align
        self._buttons: dict[Any,MultitoggleButton] = {}
        self._onChange = []
        self._lock = RLock()

        self.construct()

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        self.reconstruct()
        self._changed = True

    @property
    def background_active(self):
        return self._background_active

    @background_active.setter
    def background_active(self, value):
        self._background_active = value
        self.reconstruct()
        self._changed = True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.reconstruct()
        self._changed = True

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, value):
        self._border = value
        self.reconstruct()
        self._changed = True

    @property
    def text_align(self):
        return self._text_align

    @text_align.setter
    def text_align(self, value):
        self._text_align = value
        self.reconstruct()
        self._changed = True

    @property
    def gap(self):
        return self._gap

    @gap.setter
    def gap(self, value):
        self._gap = value
        self.reconstruct()
        self._changed = True


    @property
    def buttons(self):
        return [btn for btn in self._buttons.values()]

    @property
    def value(self):
        if self.selected_index is None:
            return None
        return self._values[self.selected_index]

    def reconstruct(self):
        with self._lock:
            self.destruct()
            self.construct()

    def construct(self):
        if len(self._buttons) > 0:
            raise Exception("Multitoggle already constructed")

        for key, value in self._values.items():
            bg = self._background_active if key == self.selected_index else self._background
            self._buttons[key] = MultitoggleButton(
                key, value, self.eventHandler, self._font, background=bg, color=self._color, 
                border_color=self._border, padding=self._btn_padding, text_align=self._text_align
            )
            self._buttons[key].addEventListener("mouseClick", self._onClick)

    async def _onClick(self, e: object):
        btn: MultitoggleButton = e.target
        if btn.key == self.selected_index:
            return

        self.selected_index = btn.key
        e.value = btn.key
        for f in self._onChange:
            params = inspect.signature(f).parameters
            if inspect.iscoroutinefunction(f):
                if len(params) == 1:
                    await f(e)
                else:
                    await f()
            else:
                if len(params) == 1:
                    f(e)
                else:
                    f()

    def destruct(self):
        for btn in self._buttons.values():
            btn.destruct()
        self._buttons = {}

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
        
        if not self.visible:
            return 0
        self._width = value

        l = len(self._buttons)
        btn_width = (self.innerwidth - (l-1) * self._gap) / l
        for btn in self._buttons.values():
            btn.width = btn_width

    @property
    def height(self):
        if self._height is None:
            return get_outerheight(self._calc_innerheight(), self.padding)
        return self._height

    @height.setter
    def height(self, value):
        if value is None:
            self._height = None
            return
        if value < 0:
            raise ValueError("height cannot be negative")
        
        if not self.visible:
            return 0
        self._height = value

        for btn in self._buttons.values():
            btn.height = self.innerheight

    def addEventListener(self, type, f):
        if type == "change":
            self._onChange.append(f)
        else:
            raise ValueError("Invalid event type for Multitoggle")

    def _calc_innerwidth(self):
        w = (len(self._buttons)-1) * self._gap
        for btn in self._buttons.values():
            btn.width = None # force recalculation
            w += btn.width
        return w

    def _calc_innerheight(self):
        h = 0
        for btn in self._buttons.values():
            btn.height = None # force recalculation
            h = max(h, btn.height) 
        return h

    def render(self, surface: Surface|None = None):
        frame_surface = Surface(
            (self.width, self.height), SRCALPHA, 32
        )

        x = self.padding.left
        for btn in self._buttons.values():#
            if self.selected_index is None:
                btn._background = self._background
            else:
                btn._background = self._background_active if btn.key == self.selected_index else self._background
            btn.height = self.innerheight

        with self._lock:
            sfcs = [(key, btn.render()) for key, btn in self._buttons.items()]

        for key, sfc in sfcs:
            self._buttons[key].setOffset(Vector2(x, self.padding.top) + self.absolute_offset)
            frame_surface.blit(sfc, (x, self.padding.top))
            x += sfc.get_width() + self._gap

        if surface is not None:
            surface.blit(frame_surface, self.absolute_offset)

        return frame_surface

    def setOffset(self, offset: Vector2):
        self.absolute_offset: Vector2 = offset