from typing import SupportsFloat, SupportsInt
from pyscreen.settings import MAX_SCALE, MIN_SCALE

class Scale(SupportsFloat, SupportsInt):
    def __init__(self, scale_factor):
        if isinstance(scale_factor, __class__):
            self.scale_factor = scale_factor.scale_factor
        else:
            self.scale_factor = scale_factor

        if self.scale_factor > MAX_SCALE:
            self.scale_factor = MAX_SCALE
        if self.scale_factor < MIN_SCALE:
            self.scale_factor = MIN_SCALE


    def __float__(self):
        return float(self.scale_factor)
    
    def __int__(self):
        return int(self.scale_factor)

    def __mul__(self, rhs: int|float):
        return self.scale_factor * rhs

    def __rmul__(self, lhs: int|float):
        return self.scale_factor * lhs

    def __truediv__(self, rhs: int|float):
        return self.scale_factor / rhs

    def __rtruediv__(self, lhs: int|float):
        return lhs / self.scale_factor

    def __lt__(self, rhs: int|float):
        return self.scale_factor < rhs

    def __gt__(self, rhs: int|float):
        return self.scale_factor > rhs

    def __le__(self, rhs: int|float):
        return self.scale_factor <= rhs

    def __ge__(self, rhs: int|float):
        return self.scale_factor >= rhs

    def __eq__(self, rhs: int|float):
        return self.scale_factor == rhs

    def __ne__(self, rhs: int|float):
        return self.scale_factor != rhs


    def __hash__(self) -> int:
        return hash(self.scale_factor)