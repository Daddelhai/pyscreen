from pyscreen.core.typing import SupportsSize

_PADDING_T = tuple[int|float, int|float, int|float, int|float]

class PaddingInterface:
    def __init__(self, sizeProvider: SupportsSize, padding: _PADDING_T):
        self._padding_top = padding[0]
        self._padding_right = padding[1]
        self._padding_bottom = padding[2]
        self._padding_left = padding[3]

        self._sizeProvider = sizeProvider

    def raw(self) -> _PADDING_T:
        return (self._padding_top, self._padding_right, self._padding_bottom, self._padding_left)

    def get(self) -> _PADDING_T:
        return (self.top, self.right, self.bottom, self.left)

    @property
    def top(self) -> int:
        padding_top = self._padding_top
        if padding_top < 1 and padding_top > 0:
            padding_top = padding_top * self._sizeProvider.height
        return int(padding_top)
    
    @top.setter
    def top(self, value: int|float):
        assert value >= 0, "PaddingInterface value must be positive"
        self._padding_top = value

    @property
    def right(self) -> int:
        padding_right = self._padding_right
        if padding_right < 1 and padding_right > 0:
            padding_right = padding_right * self._sizeProvider.width
        return int(padding_right)
    
    @right.setter
    def right(self, value: int|float):
        assert value >= 0, "PaddingInterface value must be positive"
        self._padding_right = value

    @property
    def bottom(self) -> int:
        padding_bottom = self._padding_bottom
        if padding_bottom < 1 and padding_bottom > 0:
            padding_bottom = padding_bottom * self._sizeProvider.height
        return int(padding_bottom)
    
    @bottom.setter
    def bottom(self, value: int|float):
        assert value >= 0, "PaddingInterface value must be positive"
        self._padding_bottom = value

    @property
    def left(self) -> int:
        padding_left = self._padding_left
        if padding_left < 1 and padding_left > 0:
            padding_left = padding_left * self._sizeProvider.width
        return int(padding_left)
    
    @left.setter
    def left(self, value: int|float):
        assert value >= 0, "PaddingInterface value must be positive"
        self._padding_left = value

    @property
    def width(self) -> int:
        return self.left + self.right
    
    def __getitem__(self, key):
        if key == 0:
            return self._padding_top
        if key == 1:
            return self._padding_right
        if key == 2:
            return self._padding_bottom
        if key == 3:
            return self._padding_left
        raise IndexError("PaddingInterface index out of range")
    
    def __setitem__(self, key, value):
        assert value >= 0, "PaddingInterface value must be positive"

        if key == 0:
            self._padding_top = value
        elif key == 1:
            self._padding_right = value
        elif key == 2:
            self._padding_bottom = value
        elif key == 3:
            self._padding_left = value
        else:
            raise IndexError("PaddingInterface index out of range")


def get_padding(width, height, padding: _PADDING_T) -> _PADDING_T:
    padding_top = padding[0]
    padding_right = padding[1]
    padding_bottom = padding[2]
    padding_left = padding[3]

    if padding_top < 1 and padding_top > 0:
        padding_top = padding_top * height
    if padding_right < 1 and padding_right > 0:
        padding_right = padding_right * width
    if padding_bottom < 1 and padding_bottom > 0:
        padding_bottom = padding_bottom * height
    if padding_left < 1 and padding_left > 0:
        padding_left = padding_left * width

    return (int(padding_top), int(padding_right), int(padding_bottom), int(padding_left))

def get_padding_from_inner(innerwidth: int|float, innerheight: int|float, padding: _PADDING_T) -> _PADDING_T:
    padding_top = padding[0]
    padding_right = padding[1]
    padding_bottom = padding[2]
    padding_left = padding[3]

    outerwidth = __get_outer_from_inner(innerwidth, padding_left, padding_right)
    outerheight = __get_outer_from_inner(innerheight, padding_top, padding_bottom)

    if padding_top < 1 and padding_top > 0:
        padding_top = padding_top * outerheight
    if padding_right < 1 and padding_right > 0:
        padding_right = padding_right * outerwidth
    if padding_bottom < 1 and padding_bottom > 0:
        padding_bottom = padding_bottom * outerheight
    if padding_left < 1 and padding_left > 0:
        padding_left = padding_left * outerwidth

    return (int(padding_top), int(padding_right), int(padding_bottom), int(padding_left))

def get_outerwidth(innerwidth: int|float, padding: _PADDING_T) -> int|float:
    padding_right = padding[1]
    padding_left = padding[3]

    return __get_outer_from_inner(innerwidth, padding_left, padding_right)

def get_outerheight(innerheight: int|float, padding: _PADDING_T) -> int|float:
    padding_top = padding[0]
    padding_bottom = padding[2]

    return __get_outer_from_inner(innerheight, padding_top, padding_bottom)

def get_innerwidth(outerwidth: int|float, padding: _PADDING_T) -> int|float:
    padding_right = padding[1]
    padding_left = padding[3]

    return __get_inner_from_outer(outerwidth, padding_left, padding_right)

def get_innerheight(outerheight: int|float, padding: _PADDING_T) -> int|float:
    padding_top = padding[0]
    padding_bottom = padding[2]

    return __get_inner_from_outer(outerheight, padding_top, padding_bottom)

def __get_outer_from_inner(inner: int|float, p1: int|float, p2: int|float) -> int|float:
    iw = inner
    iw_q = 1

    if p1 >= 1:
        iw = iw + p1
    else:
        iw_q -= p1

    if p2 >= 1:
        iw = iw + p2
    else:
        iw_q -= p2

    return iw / iw_q

def __get_inner_from_outer(outer: int|float, p1: int|float, p2: int|float) -> int|float:
    iw = outer

    if p1 >= 1:
        iw -= p1
    else:
        iw -= p1 * outer

    if p2 >= 1:
        iw -= p2
    else:
        iw -= p2 * outer

    return iw