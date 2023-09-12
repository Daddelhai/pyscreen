from pygame import SRCALPHA, Surface

from pyscreen.core.vector import Vector2
from pyscreen.core.typing import SupportsSize
from pyscreen.drawobj.util.background import BackgroundImage
from ._util.margin import MarginInterface, width_from_outer, height_from_outer

from .box import Box, HorizontalBox

# sizeProvider: provider for width and height
# margin: provider for margin in pixels (positive int) or percentage (float between 0 and 1)
# padding: provider for padding in pixels (positive int) or percentage (float between 0 and 1)

FLEX_BOX_MIN_HEIGHT = 50


class Flexbox(Box):
    """ Like a HTML Div """

    def __init__(self, sizeProvider: SupportsSize=None, objects: list|None = None, location: Vector2|tuple = (0,0), margin: Vector2|tuple = (0,0,0,0), padding: tuple = (0,0,0,0), gap: int = 1,
        alignment: str = "stretch", background: None|tuple|BackgroundImage = None, height: int|None = None, width: int|None = None
    ):
        super().__init__(padding=padding)
        self._sizeProvider = sizeProvider
        self._width = width
        self._height = height

        if self._sizeProvider is not None:
            self._margin = MarginInterface(sizeProvider, margin)
        else:
            self._margin = MarginInterface(self, margin)

        self._scoll_height = 0
        self._visible = True

        alignment = alignment.lower()
        if alignment not in ('left', 'right', 'center', 'stretch'):
            raise ValueError("invalid alignment: '%s'" % alignment)
        self._alignment = alignment
        self._background = background
        self._gap = gap
        self._location = Vector2(location)
        self.absolute_offset = Vector2(0,0)

        self._objects: list = list(objects) if objects is not None else []
        self._obj_sizes: dict[int,tuple[int,int]] = {}
        self._obj_surf_pos: dict[int,tuple[int,int]] = {}
        self._surface = Surface((self.width, self.height), SRCALPHA, 32)

    @property
    def margin(self):
        return super().margin
    
    @margin.setter
    def margin(self, value):
        if self._sizeProvider is not None:
            self._margin = MarginInterface(self._sizeProvider, value)
        else:
            self._margin = MarginInterface(self, value)
        self._changed = True

    @property
    def height(self):
        if not self._visible:
            return 0
        if self._height is not None:
            return self._height
        
        if self._sizeProvider is not None:
            return height_from_outer(self._sizeProvider, self.margin)
        
        return self.innerheight + self.padding.top + self.padding.bottom
    
    @height.setter
    def height(self, value):
        if value is None:
            self._height = None
            return
        if value < 0:
            raise ValueError("height cannot be negative")
        self._height = value
        self._changed = True

    @property
    def innerheight(self):
        if not self._visible:
            return 0
        if self._height is not None:
            return self._height - self.padding.top - self.padding.bottom
        
        if self._sizeProvider is not None:
            return max(self.height - self.padding.top - self.padding.bottom, 0)
        
        return max(self._calc_innerheight(), 0) 
    
    @property
    def width(self):
        if not self._visible:
            return 0
        if self._width is not None:
            return self._width
        
        if self._sizeProvider is not None:
            return width_from_outer(self._sizeProvider, self.margin)
        
        return self.innerwidth + self.padding.left + self.padding.right
    
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
    def innerwidth(self):
        if not self._visible:
            return 0
        if self._width is not None:
            return self._width - self.padding.left - self.padding.right
        
        if self._sizeProvider is not None:
            return max(self.width - self.padding.left - self.padding.right, 0)
        
        return max(self._calc_innerwidth(), 0)
        

class HorizontalFlexbox(HorizontalBox):
    """ Like a HTML Div but horizontal """

    def __init__(self, sizeProvider: SupportsSize=None, objects: list|None = None, location: Vector2|tuple = (0,0), margin: Vector2|tuple = (0,0,0,0), padding: tuple = (0,0,0,0), gap: int = 1,
        alignment: str = "stretch", background: None|tuple|BackgroundImage = None, height: int|None = None, width: int|None = None
    ):
        super().__init__(padding=padding)
        self._sizeProvider = sizeProvider
        self._width = width
        self._height = height

        self.margin = MarginInterface(sizeProvider, margin)

        self._scoll_height = 0
        self._visible = True

        alignment = alignment.lower()
        if alignment not in ('top', 'bottom', 'center', 'stretch'):
            raise ValueError("invalid alignment: '%s'" % alignment)
        self._alignment = alignment
        self._background = background
        self._gap = gap
        self._location = Vector2(location)
        self.absolute_offset = Vector2(0,0)

        self._objects: list = list(objects) if objects is not None else []
        self._obj_sizes: dict[int,tuple[int,int]] = {}
        self._obj_surf_pos: dict[int,tuple[int,int]] = {}
        self._surface = Surface((self.width, self.height), SRCALPHA, 32)

    @property
    def height(self):
        if not self._visible:
            return 0
        if self._height is not None:
            return self._height
        
        if self._sizeProvider is not None:
            return self._sizeProvider.height - self.margin.top - self.margin.bottom
        
        return self.innerheight + self.padding.top + self.padding.bottom
    
    @height.setter
    def height(self, value):
        if value is None:
            self._height = None
            return
        if value < 0:
            raise ValueError("height cannot be negative")
        self._height = value
        self._changed = True

    @property
    def innerheight(self):
        if not self._visible:
            return 0
        if self._height is not None:
            return self._height - self.padding.top - self.padding.bottom
        
        if self._sizeProvider is not None:
            return max(self.height - self.padding.top - self.padding.bottom, 0)
        
        return max(self._calc_innerheight(), 0) 
    
    @property
    def width(self):
        if not self._visible:
            return 0
        if self._width is not None:
            return self._width
        
        if self._sizeProvider is not None:
            return self._sizeProvider.width - self.margin.left - self.margin.right
        
        return self.innerwidth + self.padding.left + self.padding.right
    
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
    def innerwidth(self):
        if not self._visible:
            return 0
        if self._width is not None:
            return self._width - self.padding.left - self.padding.right
        
        if self._sizeProvider is not None:
            return max(self._sizeProvider.width - self.padding.left - self.padding.right \
                - self.margin.left - self.margin.right, 0)
        
        return max(self._calc_innerwidth(), 0)
        

