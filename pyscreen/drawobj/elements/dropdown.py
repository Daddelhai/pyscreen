from typing import overload

from pygame.font import Font
from pygame import Surface

from pyscreen.core.vector import Vector2
from pyscreen.eventHandler import EventHandler
from pyscreen.screen import Screen

from ._dropdown.box import DropDownBox
from ._dropdown.popup import DropDownPopup
from .base import Element

###################################################################
###################################################################


class Dropdown(Element):
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

    def __init__(self, screen: Screen, eventHandler: EventHandler, font: Font, *, location: tuple|Vector2 = (0,0),
                  width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                  border_color=None, placeholder="Select...", padding=(2,8,2,8), margin=(0,0,0,0), options:list|dict|None = None):
        
        self.screen = screen
        self.font = font
        self.frameelement = None
        self._width = width
        self._visible = True
        self.placeholder = placeholder
        self.popup = DropDownPopup(screen, eventHandler, font, options, background, color, border_color)
        self.box = DropDownBox(eventHandler, font, location, width, height, background, color, border_color, placeholder, padding, margin)
        self.box.addEventListener("mouseClick", self.focus)
        self.__click_handler = None

        super().__init__(eventHandler, padding, margin, width, height)

        screen.add_popup(self.popup)

    @property
    def changed(self):
        return self.box.changed

    @property
    def value(self):
        return self.popup.selected_value
    
    @property
    def selected_index(self):
        return self.popup.selected_index

    @selected_index.setter
    def selected_index(self, value):
        self.popup.selected_index = value
        if value is None:
            self.box.value = self.placeholder
        else:
            self.box.value = self.popup.selected_value

    @property
    def options(self):
        return self.popup.options

    @options.setter
    def options(self, value):
        self.popup.options = value

    def destruct(self):
        self.screen.remove_popup(self.popup)
        self.box.destruct()
        self.popup.destruct()

    async def focus(self, e = None):
        await self.box.focus(e)
        pos = self.location + self.absolute_offset + (0,self.height)
        width = self._width if self._width is not None else self.popup.max_width()
        self.popup.open(pos, width)
        self.popup.onSelect = self.select

        async def wrapper(e):
            await self.box.releaseFocus()
            self.popup.close()
            if self.__click_handler is not None:
                if self.eventHandler.removeEventListener(self.__click_handler) == 0:
                    raise RuntimeError("Cannot remove click handler in DropDown")
                self.__click_handler = None

        if self.__click_handler is None:
            self.__click_handler =\
                self.eventHandler.addEventListener("mouseClick", wrapper, override=True)

    def select(self, e):
        self.popup.selected_index = e.target.key
        self.box.value = e.target.value

    @property
    def absolute_offset(self):
        return self.box.absolute_offset

    @absolute_offset.setter
    def offset(self, value: Vector2):
        self.box.absolute_offset: Vector2 = value


    def render(self, surface:Surface|None=None):
        if not self.visible:
            return
        return self.box.render(surface)

    @property
    def width(self):
        return self.box.width
    
    @width.setter
    def width(self, width):
        if width is None:
            self._width = None
            self.box.width = None
            return
        if width < 0:
            raise ValueError("width cannot be negative")
        self._width = width
        self.box.width = width
        self._changed = True

    @property
    def height(self):
        return self.box.height

    @property
    def location(self):
        return self.box.location

    @location.setter
    def location(self, value):
        self.box.location = value

    def setOffset(self, offset: Vector2):
        self.box.setOffset(offset)

    def addEventListener(self, event, callback):
        self.box.addEventListener(event, callback)

    def removeEventListener(self, future):
        self.box.removeEventListener(future)

    @property
    def padding(self):
        return self.box.padding
    
    @padding.setter
    def padding(self, value):
        self.box.padding = value
    
    @property
    def margin(self):
        return self.box.margin
    
    @margin.setter
    def margin(self, value):
        self.box.margin = value