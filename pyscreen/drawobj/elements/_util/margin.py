from pyscreen.core.typing import SupportsSize

_MARGIN_T = tuple[int|float, int|float, int|float, int|float]

class MarginInterface:
    def __init__(self, sizeProvider: SupportsSize, margin: _MARGIN_T):
        self._margin_top = margin[0]
        self._margin_right = margin[1]
        self._margin_bottom = margin[2]
        self._margin_left = margin[3]

        self._sizeProvider = sizeProvider

    def raw(self) -> _MARGIN_T:
        return (self._margin_top, self._margin_right, self._margin_bottom, self._margin_left)
    
    def get(self) -> _MARGIN_T:
        return (self.top, self.right, self.bottom, self.left)

    @property
    def top(self) -> int:
        margin_top = self._margin_top
        if margin_top < 1 and margin_top > 0:
            margin_top = margin_top * self._sizeProvider.height
        return int(margin_top)
    
    @top.setter
    def top(self, value: int|float):
        assert value >= 0, "MarginInterface value must be positive"
        self._margin_top = value

    @property
    def right(self) -> int:
        margin_right = self._margin_right
        if margin_right < 1 and margin_right > 0:
            margin_right = margin_right * self._sizeProvider.width
        return int(margin_right)

    @right.setter
    def right(self, value: int|float):
        assert value >= 0, "MarginInterface value must be positive"
        self._margin_right = value

    @property
    def bottom(self) -> int:
        margin_bottom = self._margin_bottom
        if margin_bottom < 1 and margin_bottom > 0:
            margin_bottom = margin_bottom * self._sizeProvider.height
        return int(margin_bottom)
    
    @bottom.setter
    def bottom(self, value: int|float):
        assert value >= 0, "MarginInterface value must be positive"
        self._margin_bottom = value

    @property
    def left(self) -> int:
        margin_left = self._margin_left
        if margin_left < 1 and margin_left > 0:
            margin_left = margin_left * self._sizeProvider.width
        return int(margin_left)
    
    @left.setter
    def left(self, value: int|float):
        assert value >= 0, "MarginInterface value must be positive"
        self._margin_left = value

    @property
    def width(self) -> int:
        return self.left + self.right
    
    @property
    def height(self) -> int:
        return self.top + self.bottom

    def __getitem__(self, key: int) -> int:
        if key == 0:
            return self._margin_top
        if key == 1:
            return self._margin_right
        if key == 2:
            return self._margin_bottom
        if key == 3:
            return self._margin_left
        raise IndexError("MarginInterface index out of range")
    
    def __setitem__(self, key: int, value: int|float):
        assert value >= 0, "MarginInterface value must be positive"
        if key == 0:
            self._margin_top = value
        elif key == 1:
            self._margin_right = value
        elif key == 2:
            self._margin_bottom = value
        elif key == 3:
            self._margin_left = value
        else:
            raise IndexError("MarginInterface index out of range")
    
    


def width_from_outer(outerobj: SupportsSize, margin: _MARGIN_T) -> int:
    margin_right = margin[1]
    margin_left = margin[3]

    factor = 1
    subtract = 0
    if margin_right < 1 and margin_right > 0:
        factor -= margin_right
    else:
        subtract += margin_right
    if margin_left < 1 and margin_left > 0:
        factor -= margin_left
    else:
        subtract += margin_left

    relative_width = outerobj.width * factor
    return int(relative_width - subtract)

def height_from_outer(outerobj: SupportsSize, margin: _MARGIN_T) -> int:
    margin_top = margin[0]
    margin_bottom = margin[2]

    factor = 1
    subtract = 0
    if margin_top < 1 and margin_top > 0:
        factor -= margin_top
    else:
        subtract += margin_top
    if margin_bottom < 1 and margin_bottom > 0:
        factor -= margin_bottom
    else:
        subtract += margin_bottom

    relative_height = outerobj.height * factor
    return int(relative_height - subtract)
