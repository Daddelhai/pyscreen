from contextlib import contextmanager
from typing import Any, overload

import pygame
from pyscreen.core.vector import Vector2, IVector2
from pyscreen.eventHandler import EventHandler, EventListenerFuture
from pyscreen.hitbox import Hitbox
from pyscreen.core.entity import StaticEntity
from pyscreen.drawobj.elements._util.padding import get_innerheight, get_innerwidth, get_outerheight, get_outerwidth, PaddingInterface
from pyscreen.drawobj.elements._util.margin import MarginInterface
from pygame import Surface
from abc import abstractmethod

class Element(StaticEntity):
    def __init__(self, eventHandler: EventHandler|None = None, padding: tuple[int,int,int,int]|None = None, margin: tuple[int,int,int,int]|None = None, width: int|None = None, height:int|None = None):
        self.eventHandler = eventHandler
        
        self._padding: PaddingInterface = PaddingInterface(self, padding or (0,0,0,0))
        self._margin: MarginInterface = MarginInterface(self, margin or (0,0,0,0))


        self._width = width
        self._height = height

        self._visible = True
        self._changed = True
        if not hasattr(self, "offset"):
            self.offset = Vector2(0,0)

    @property
    def padding(self):
        return self._padding
    
    @padding.setter
    def padding(self, value):
        self._padding = PaddingInterface(self, value)
        self._changed = True

    @property
    def margin(self):
        return self._margin
    
    @margin.setter
    def margin(self, value):
        self._margin = MarginInterface(self, value)
        self._changed = True

    @abstractmethod
    def render(self, surface: Surface|None):
        raise NotImplementedError

    @property
    def changed(self):
        return self._changed

    @changed.setter
    def changed(self, value):
        self._changed = value

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        if value == self._visible:
            return
        self._changed = True
        self._visible = value 

    @abstractmethod
    def destruct(self):
        raise NotImplementedError

    @abstractmethod
    def setOffset(self, offset):
        raise NotImplementedError

    @property
    def innerwidth(self):
        if not self.visible:
            return 0
        if self._width is None:
            return self._calc_innerwidth()
        return get_innerwidth(self._width, self.padding)

    @property
    def settedWidth(self):
        return self._width

    @property
    def width(self):
        if not self.visible:
            return 0
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
        if not self.visible:
            return 0
        if self._height is None:
            return self._calc_innerheight()
        return get_innerheight(self._height, self.padding)

    @property
    def settedHeight(self):
        return self._height

    @property
    def height(self):
        if not self.visible:
            return 0
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
        self._changed = True
        self._height = value

    def _calc_innerwidth(self):
        raise NotImplementedError

    def _calc_innerheight(self):
        raise NotImplementedError
    
    def get_size(self) -> tuple[int,int]:
        return [self.width, self.height]
    
    def get_position(self) -> tuple[int,int]:
        """ Returns the position of the element relative to the screen. NOT THE PARENT """
        """ Required by Screen """
        if isinstance(self.offset, IVector2):
            return tuple(self.offset.asInts())
        return self.offset
    
    @contextmanager
    def resetAfter(self):
        try:
            height = self._height
            width = self._width
            yield self
        finally:
            self._height = height
            self._width = width


class ElementWithHitbox(Element):
    class EventCreator:
        class Decorator:
            def __init__(self, target, eventType, **options):
                self.target = target
                self.eventType = eventType
                self.options = options

            def __call__(self, func: callable):
                self.target.addEventListener(self.eventType, func, **self.options)
                return func

        def __init__(self, target):
            self.target = target
        
        def __call__(self, eventType: str, **options) -> Decorator:
            return self.Decorator(self.target, eventType, **options)

    @property
    def on(self):
        return self.EventCreator(self)

    def __init__(self, eventHandler: EventHandler, padding: tuple[int,int,int,int], margin: tuple[int,int,int,int], width: int|None, height:int|None):
        super().__init__(eventHandler, padding, margin, width, height)
        self.hitbox: Hitbox|None = Hitbox(eventHandler, target=self)

    def destruct(self):
        if self.hitbox is not None:
            self.hitbox.destruct()
        self.hitbox = None

    async def releaseFocus(self):
        await self.hitbox.releaseFocus()

    def setOffset(self, offset):
        self.hitbox.hitbox_location = offset

    def printHitbox(self, surface, color=(255,0,0)):
        if self.hitbox is None:
            return
        
        if self.hitbox.enabled:
            rect = pygame.Rect(
                int(self.hitbox.hitbox_location.x),
                int(self.hitbox.hitbox_location.y),
                int(self.hitbox.hitbox_size.x),
                int(self.hitbox.hitbox_size.y)
            )
            pygame.draw.rect(surface, color, rect, 1)

    def hasFocus(self):
        return self.hitbox.hasFocus

    @overload
    def addEventListener(self, event, callback) -> EventListenerFuture:
        ...
    @overload
    def addEventListener(self, event, callback, *, once: bool = False, key: Any | None = None, key_mods: list | None = None, override: bool = False) -> EventListenerFuture:
        ...
    def addEventListener(self, event, callback, *, once: bool = False, key: Any | None = None, key_mods: list | None = None, override: bool = False) -> EventListenerFuture:
        return self.hitbox.addEventListener(event, callback, once, key, key_mods, override)

    def removeEventListener(self, future: EventListenerFuture):
        self.hitbox.removeEventListener(future)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        if value == self._visible:
            return
        self._changed = True
        self.hitbox.enabled = value
        self._visible = value 