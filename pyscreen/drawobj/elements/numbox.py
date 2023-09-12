from time import time

from pygame import (K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9,
                    K_BACKSPACE, K_DOWN, K_RETURN, K_UP, K_MINUS,
                    K_COMMA, K_PERIOD, SRCALPHA, Surface)
from pygame.font import Font

import pyscreen.drawobj.draw as draw
from pyscreen.core.vector import Vector2
from pyscreen.eventHandler import EventHandler
from pyscreen.hitbox import Hitbox

from .textbox import Textbox

from pyscreen.logging import getLogger
logger = getLogger()

class Numbox(Textbox):
    def __init__(self, eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, value:int|float=0, max=None, min=None, padding=(2,8,2,8), margin=(0,0,0,0), step:int|float=1, placeholder:str=""):
        
        self.hitbox: Hitbox = Hitbox(eventHandler,target=self)
        super().__init__(eventHandler, font, location, width, height, background, color, border_color, padding=padding, margin=margin, placeholder=placeholder)
        self._str_value = str(value)
        self._num_value = value
        self.max = max
        self.min = min
        self.step = step

        self.hitbox.addEventListener("mouseClick", self.focus)

        self.__override_event = None

    @property
    def value(self):
        return self._num_value
    
    @property
    def _show_value(self) -> str:
        return self._str_value

    @value.setter
    def value(self, value: int|float):
        self._changed = True
        self._update_num_value(value)
        self._update_str_value(self._num_value)

    async def _onKeydown(self, event):
        if event.key == K_BACKSPACE:
            if len(self._str_value) > 0:
                self._str_value = self._str_value[:-1]
                self._update_num_value(self._str_value)
            
        elif event.key == K_RETURN:
            await self.hitbox.releaseFocus()

        elif self.max_length is None or len(self.value) < self.max_length:
            if event.key in (K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0, K_MINUS):
                self._str_value = self._str_value + event.unicode
                self._update_num_value(self._str_value)
            if event.key in (K_PERIOD, K_COMMA):
                self._str_value = self._str_value + "." if "." not in self._str_value else self._str_value
            if event.key == K_UP:
                if self._num_value is not None:
                    self._num_value = self._num_value + self.step
                    if self.max is not None and self._num_value > self.max:
                        self._num_value = self.max
                    self._update_str_value(self._num_value)
            if event.key == K_DOWN:
                if self._num_value is not None:
                    self._num_value = self._num_value - self.step
                    if self.min is not None and self._num_value < self.min:
                        self._num_value = self.min
                    self._update_str_value(self._num_value)

    def _update_num_value(self, value: int|float|str|None):
        self._changed = True
        if value is None:
            self._num_value = None
            return
        if isinstance(value, (int,float)):
            self._num_value = value
        elif isinstance(value, str):
            if value.isdecimal() or value.isdigit():
                try:
                    if "." in value:
                        self._num_value = float(value)
                    else:
                        self._num_value = int(value)
                except ValueError:
                    self._num_value = None
                    return
            else:
                self._num_value = None
                return
        else:
            raise TypeError(f"Invalid type for value: {type(value)}")

        if self.max is not None and self._num_value > self.max:
            self._num_value = self.max
            return
        if self.min is not None and self._num_value < self.min:
            self._num_value = self.min
            return

        if isinstance(self._num_value, float):
            self._num_value = round(self._num_value, 5)
            

    def _update_str_value(self, value: int|float|None):
        self._changed = True
        if value is None:
            self._str_value = ""
            return
        elif isinstance(value, float):
            if self.value.is_integer():
                self._str_value = str(int(value))
                return
        self._str_value = str(value)


    async def focus(self, e):
        if not self.hitbox.hasFocus:
            await self.hitbox.focus(lambda: self.value)
            if self.__override_event is None:
                self.__override_event = self.hitbox.outer.addEventListener("keyDown", self._onKeydown, override=True)
                def leave(e):
                    self._update_str_value(self._num_value)
                    assert self.hitbox.removeEventListener(self.__override_event) > 0
                    self.__override_event = None
                self.hitbox.addEventListener("focusRelease", leave, True)
        

