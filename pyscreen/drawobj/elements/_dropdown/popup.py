import numpy as np
from pygame import Surface, SRCALPHA
from pyscreen.core.vector import Vector2
from pyscreen.hitbox import Hitbox
from pyscreen.eventHandler import EventHandler
from pyscreen.screen import Screen
from pygame.font import Font

from ..base import Element
from .option import DropDownOption

from pyscreen.logging import getLogger
logger = getLogger()

class DropDownPopup(Element):
    # Uses custom hitbox logic => no ElementWithHitbox
    def __init__(self, screen: Screen, eventHandler: EventHandler, font: Font, options: list|dict|None, background, color, border_color, selected_index = None):
        self.eventHandler = eventHandler
        self.screen = screen
        self._visible = False
        self._options = [] if options is None else options
        self.location = None
        self._width = None
        self._height = None
        self.surface = None
        self.background = background
        self.border_color = border_color
        self.color = color
        self.font = font
        self.offset = Vector2(0,0)
        self._selected_index = selected_index

        self.scroll_height = 0

        self.max_width_cache = None

        self.buttons: list[DropDownOption] = []
        self.listener = []

        self.hitbox = None

    @property
    def selected_index(self):
        return self._selected_index

    @selected_index.setter
    def selected_index(self, key):
        if key is None:
            self._selected_index = None
            return
        if self.options is None:
            raise ValueError("Cannot set selected index if options is None")
        if isinstance(self.options, (dict,set)):
            if key not in self.options:
                raise ValueError(f"Invalid key {key}")
        else:
            # list or tuple
            if key < 0 or key >= len(self.options):
                raise ValueError(f"Invalid index {key}")
        self._selected_index = key

    @property
    def selected_value(self):
        if self.options is None or self.selected_index is None:
            return None
        if isinstance(self.options, set):
            return self.selected_index
        return self.options[self.selected_index]

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self.max_width_cache = None
        self._options = value

        # Check if selected index is still valid
        if self.selected_index is not None:
            if isinstance(self.options, (dict,set)):
                if self.selected_index not in self._options:
                    self.selected_index = None
            else:
                self.selected_index = None

    @property
    def onSelect(self):
        pass

    @onSelect.setter
    def onSelect(self, value):
        for button in self.buttons:
            button.addEventListener("mouseClick", value, override=True)

    def max_width(self):
        if self.max_width_cache is None:
            if not self.options:
                self.max_width_cache = 0
            elif isinstance(self.options, dict):
                self.max_width_cache = max(DropDownOption(key,option,self.eventHandler,self.font).width for key, option in self.options.items()) + 30
            else:
                self.max_width_cache = max(DropDownOption(0,option,self.eventHandler,self.font).width for option in self.options) + 30
        return self.max_width_cache

    def open(self, location: Vector2, width: int):
        self.location = location
        self.width = width
        self.build()
        self._visible = True

    def close(self):
        self._visible = False
        self.destruct()
        for listener in self.listener:
            if self.eventHandler.removeEventListener(listener) == 0:
                raise RuntimeError("Cannot remove click handler in _DropDownPopup")
    
    def destruct(self):
        for button in self.buttons:
            button.destruct()
        self.buttons = []
        if self.hitbox is not None:
            self.hitbox.destruct()
        self.hitbox = None

    def build(self):
        self.max_avail_width = self.screen.get_size()[0] - self.location[0]
        self.max_avail_height = self.screen.get_size()[1] - self.location[1]

        space: Vector2 = Vector2(self.max_avail_width, self.max_avail_height)

        self.surface = Surface(tuple(self.location.asInts()),SRCALPHA,32)
        if self.hitbox is None:
            self.hitbox = Hitbox(self.eventHandler, self.location, space)
            # Scroll events
        else:
            self.hitbox.hitbox_location = self.location
            self.hitbox.hitbox_size = space

        if isinstance(self.options, dict):
            for key, option in self.options.items():
                option = DropDownOption(key,option,self.eventHandler,self.font,
                    background=self.background, color=self.color,
                    border_color=self.border_color, width=self.width)
                self.buttons.append(option)
        elif isinstance(self.options, set):
            for option in self.options:
                option = DropDownOption(option,option,self.eventHandler,self.font,
                    background=self.background, color=self.color,
                    border_color=self.border_color, width=self.width)
                self.buttons.append(option)
        else:
            for key, option in enumerate(self.options):
                option = DropDownOption(key,option,self.eventHandler,self.font,
                    background=self.background, color=self.color,
                    border_color=self.border_color, width=self.width)
                self.buttons.append(option)

        
    def render(self, surface):
        if self._visible:
            if self.surface is None:
                logger.warn("Surface is NONE in _DropDownPopup")
                self.close()
                return

            if self.location is None:
                logger.warn("Location is NONE in _DropDownPopup")
                self.close()
                return                

            position = self.location + self.offset
            h = 0

            for button in self.buttons:
                button.location = self.location + (0,h)
                h += button.height - 1
                button.width = self.width
                button.render(surface)
            
            

            