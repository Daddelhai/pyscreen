import numpy

PI = 3.141592653589793238462643383279502884197169399375105820974944592307816406286
PI2 = PI * 2


cdef class Angle:

    def __init__(self, angle_rad: double = 0):
        self.rad = angle_rad % (PI2)

        if self.rad < 0:
            self.rad += PI2

    @classmethod
    def fromRad(cls, angle: double):
        return cls(angle)

    @classmethod
    def fromDeg(cls, angle: double):
        return cls(angle * numpy.pi / 180)


    @property
    def rad(self):
        return self._radians

    @property
    def deg(self):
        return self._radians * 180 / numpy.pi



    @rad.setter
    def rad(self, angle: double):
        self._radians = angle

    @deg.setter
    def deg(self, angle: double):
        self._radians = angle * numpy.pi / 180


    def __add__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return Angle(self.rad + other.rad)

    def __sub__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return Angle(self.rad - other.rad)

    def __eq__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return int(self.rad * 10) == int(other.rad * 10)

    def __ne__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return int(self.rad * 10) != int(other.rad * 10)

    def __lt__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return self.rad < other.rad

    def __gt__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return self.rad > other.rad

    def __le__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return self.rad <= other.rad

    def __ge__(self, other):
        if isinstance(other, int):
            other = Angle.fromDeg(other)
        return self.rad >= other.rad


    def __mul__(self, o: double):
        return Angle(self.rad * o)

    def __rmul__(self, o: double):
        return Angle(self.rad * o)

    def __truediv__(self, o: double):
        return Angle(self.rad / o)


    def __float__(self):
        return float(self.rad)

    def __int__(self):
        return int(self.deg)


    def __neg__(self):
        return Angle(-self.rad)
    

    def __str__(self) -> str:
        if self.deg == 0:
            return "360"
        return str(int(self))

    def __hash__(self) -> int:
        return hash(self.deg)