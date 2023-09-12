from functools import lru_cache
from libc.math cimport sqrt, atan2, sin, cos, tan
from pyscreen.core.angle import Angle, PI
from typing import SupportsFloat, SupportsInt, overload

cdef class Vector2:
    def __init__(self, x, y = None):
        if y is None:
            self.__init__(x[0],x[1])
            return
        
        self.x = x
        self.y = y
        self.__hash = hash((self.x,self.y))

    property x:
        def __get__(self):
            return self.m_x

        def __set__(self, value):
            self.m_x = value
            self.__hash = hash((self.x,self.y))

    property y:
        def __get__(self):
            return self.m_y

        def __set__(self, value):
            self.m_y = value
            self.__hash = hash((self.x,self.y))

    def asInts(self):
        return IntVector2(
            <long>self.x,
            <long>self.y
        )

    def asFloats(self):
        return Vector2(
            <double>self.x,
            <double>self.y
        )


    def r90(self):
        """Rotate 90 degrees left"""
        return Vector2(-self.y, self.x)

    def l90(self):
        """Rotate 90 degrees right"""
        return Vector2(self.y, -self.x)

    @lru_cache(maxsize=1_000_000)
    def angleBetween(self, other):
        """Get the angle between two vectors counterclockwise"""
        dp = self.dotProduct(other)
        cp = self.crossProduct(other)

        return Angle.fromRad(atan2(cp, dp) + PI)

    def __str__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, index):
        if index in (0,"x"):
            return self.x
        elif index in (1,"y"):
            return self.y
        else:
            raise IndexError("Unknown index for Vector2 object")

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    def __ne__(self, other):
        return self.x != other[0] or self.y != other[1]

    @lru_cache(maxsize=1_000_000)
    def __add__(self, other):
        return Vector2(self.x + other[0], self.y + other[1])

    __radd__ = __add__

    @lru_cache(maxsize=1_000_000)
    def __sub__(self, other):
        return Vector2(self.x - other[0], self.y - other[1])

    @lru_cache(maxsize=1_000_000)
    def __rsub__(self, other):
        return Vector2(other[0] - self.x, other[1] - self.y)

    @lru_cache(maxsize=1_000_000)
    def __truediv__(self, other):
        if isinstance(other, (int,float,SupportsFloat,SupportsInt)):
            return Vector2(self.x / other, self.y / other)
        return Vector2(self.x / other[0], self.y / other[1])

    @lru_cache(maxsize=1_000_000)
    def __rtruediv__(self, other):
        if isinstance(other, (int,float,SupportsFloat,SupportsInt)):
            return Vector2(other / self.x, other / self.y)
        return Vector2(other[0] / self.x, other[1] / self.y)

    @lru_cache(maxsize=1_000_000)
    def __mul__(self, other):
        if isinstance(other, (int,float,SupportsFloat,SupportsInt)):
            return Vector2(self.x * other, self.y * other)
        return Vector2(self.x * other[0], self.y * other[1])

    __rmul__ = __mul__

    def __len__(self):
        return int(self.length())

    @lru_cache(maxsize=1_000_000)
    def length(self):
        return sqrt(self.x**2 + self.y**2)

    def __hash__(self) -> int:
        return self.__hash

    @lru_cache(maxsize=1_000_000)
    def dotProduct(self, other):
        return self.x * other[0] + self.y * other[1]

    @lru_cache(maxsize=1_000_000)
    def crossProduct(self, other):
        return self.x * other[1] - self.y * other[0]

    def __neg__(self):
        return Vector2(-self.x, -self.y)


cdef class Vector3:
    def __init__(self, x, y = None, z = None):
        if z is None:
            self.__init__(*x)
            return
        
        self.x = x
        self.y = y
        self.z = z
        self.__hash = hash((self.x,self.y,self.z))

    property x:
        def __get__(self):
            return self.m_x

        def __set__(self, value):
            self.m_x = value
            self.__hash = hash((self.x,self.y,self.z))

    property y:
        def __get__(self):
            return self.m_y

        def __set__(self, value):
            self.m_y = value
            self.__hash = hash((self.x,self.y,self.z))

    property z:
        def __get__(self):
            return self.m_z

        def __set__(self, value):
            self.m_z = value
            self.__hash = hash((self.x,self.y,self.z))

    def asInts(self):
        return IntVector3(
            <long>self.x,
            <long>self.y,
            <long>self.z
        )

    def asFloats(self):
        return Vector3(
            <double>self.x,
            <double>self.y,
            <double>self.z
        )

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, index):
        if index in (0,"x"):
            return self.x
        elif index in (1,"y"):
            return self.y
        elif index in (2,"z"):
            return self.z
        else:
            raise IndexError("Unknown index for Vector2 object")

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1] and self.z == other[2]

    def __ne__(self, other):
        return self.x != other[0] or self.y != other[1] or self.z != other[2]

    @lru_cache(maxsize=1_000_000)
    def __add__(self, other):
        return Vector3(self.x + other[0], self.y + other[1], self.z + other[2])

    __radd__ = __add__

    @lru_cache(maxsize=1_000_000)
    def __sub__(self, other):
        return Vector3(self.x - other[0], self.y - other[1], self.z - other[2])

    @lru_cache(maxsize=1_000_000)
    def __rsub__(self, other):
        return Vector3(other[0] - self.x, other[1] - self.y, other[2] - self.z)

    @lru_cache(maxsize=1_000_000)
    def __mul__(self, other):
        return Vector3(self.x * other, self.y * other, self.z * other)

    __rmul__ = __mul__

    @lru_cache(maxsize=1_000_000)
    def __truediv__(self, other):
        return Vector3(self.x / other, self.y / other, self.z / other)

    def __rtruediv__(self, other):
        return Vector3(other / self.x, other / self.y, other / self.z)

    def __len__(self):
        return int(self.length())

    @lru_cache(maxsize=1_000_000)
    def length(self):
        return sqrt(self.x**2 + sqrt(self.y**2 + self.z**2))

    def __hash__(self) -> int:
        return self.__hash

    def __str__(self) -> str:
        return f"Vector3({self.x},{self.y},{self.z})"

    @lru_cache(maxsize=1_000_000)
    def dotProduct(self, other) -> float:
        return self.x * other[0] + self.y * other[1] + self.z * other[2]

    @lru_cache(maxsize=1_000_000)
    def crossProduct(self, other):
        return Vector3(self.y * other[2] - self.z * other[1], self.z * other[0] - self.x * other[2], self.x * other[1] - self.y * other[0])
    
    @lru_cache(maxsize=1_000_000)
    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @lru_cache(maxsize=1_000_000)
    def normalize(self):
        mag = self.magnitude()
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    cdef Vector3 rotateX(self, Angle angle):
        rad = angle.rad
        cos_theta = cos(rad)
        sin_theta = sin(rad)
        y = self.y * cos_theta - self.z * sin_theta
        z = self.y * sin_theta + self.z * cos_theta
        return Vector3(self.x, y, z)

    cdef Vector3 rotateY(self, Angle angle):
        rad = angle.rad
        cos_theta = cos(rad)
        sin_theta = sin(rad)
        x = self.x * cos_theta + self.z * sin_theta
        z = -self.x * sin_theta + self.z * cos_theta
        return Vector3(x, self.y, z)

    cdef Vector3 rotateZ(self, Angle angle):
        rad = angle.rad
        cos_theta = cos(rad)
        sin_theta = sin(rad)
        x = self.x * cos_theta - self.y * sin_theta
        y = self.x * sin_theta
        return Vector3(x, y, self.z)


cdef class IntVector2:
    def __init__(self, x, y = None):
        if y is None:
            self.__init__(x[0],x[1])
            return
        
        self.x = x
        self.y = y
        self.__hash = hash((self.x,self.y))

    property x:
        def __get__(self):
            return self.m_x

        def __set__(self, value):
            self.m_x = value
            self.__hash = hash((self.x,self.y))

    property y:
        def __get__(self):
            return self.m_y

        def __set__(self, value):
            self.m_y = value
            self.__hash = hash((self.x,self.y))

    def asInts(self):
        return IntVector2(
            <long>self.x,
            <long>self.y
        )

    def asFloats(self):
        return Vector2(
            <double>self.x,
            <double>self.y
        )


    def r90(self):
        """Rotate 90 degrees left"""
        return Vector2(-self.y, self.x)

    def l90(self):
        """Rotate 90 degrees right"""
        return Vector2(self.y, -self.x)

    @lru_cache(maxsize=1_000_000)
    def angleBetween(self, other):
        """Get the angle between two vectors counterclockwise"""
        dp = self.dotProduct(other)
        cp = self.crossProduct(other)

        return Angle.fromRad(atan2(cp, dp) + PI)

    def __str__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, index):
        if index in (0,"x"):
            return self.x
        elif index in (1,"y"):
            return self.y
        else:
            raise IndexError("Unknown index for Vector2 object")

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    def __ne__(self, other):
        return self.x != other[0] or self.y != other[1]

    @lru_cache(maxsize=1_000_000)
    def __add__(self, other):
        return Vector2(self.x + other[0], self.y + other[1])

    __radd__ = __add__

    @lru_cache(maxsize=1_000_000)
    def __sub__(self, other):
        return Vector2(self.x - other[0], self.y - other[1])

    @lru_cache(maxsize=1_000_000)
    def __rsub__(self, other):
        return Vector2(other[0] - self.x, other[1] - self.y)

    @lru_cache(maxsize=1_000_000)
    def __truediv__(self, other):
        if isinstance(other, (int,float,SupportsFloat,SupportsInt)):
            return Vector2(self.x / other, self.y / other)
        return Vector2(self.x / other[0], self.y / other[1])

    @lru_cache(maxsize=1_000_000)
    def __rtruediv__(self, other):
        if isinstance(other, (int,float,SupportsFloat,SupportsInt)):
            return Vector2(other / self.x, other / self.y)
        return Vector2(other[0] / self.x, other[1] / self.y)

    @lru_cache(maxsize=1_000_000)
    def __mul__(self, other):
        if isinstance(other, (int,float,SupportsFloat,SupportsInt)):
            return Vector2(self.x * other, self.y * other)
        return Vector2(self.x * other[0], self.y * other[1])

    __rmul__ = __mul__

    def __len__(self):
        return int(self.length())

    @lru_cache(maxsize=1_000_000)
    def length(self):
        return sqrt(self.x**2 + self.y**2)

    def __hash__(self) -> int:
        return self.__hash

    @lru_cache(maxsize=1_000_000)
    def dotProduct(self, other):
        return self.x * other[0] + self.y * other[1]

    @lru_cache(maxsize=1_000_000)
    def crossProduct(self, other):
        return self.x * other[1] - self.y * other[0]

    def __neg__(self):
        return Vector2(-self.x, -self.y)



cdef class IntVector3:
    def __init__(self, x, y = None, z = None):
        if z is None:
            self.__init__(*x)
            return
        
        self.x = x
        self.y = y
        self.z = z
        self.__hash = hash((self.x,self.y,self.z))

    property x:
        def __get__(self):
            return self.m_x

        def __set__(self, value):
            self.m_x = value
            self.__hash = hash((self.x,self.y,self.z))

    property y:
        def __get__(self):
            return self.m_y

        def __set__(self, value):
            self.m_y = value
            self.__hash = hash((self.x,self.y,self.z))

    property z:
        def __get__(self):
            return self.m_z

        def __set__(self, value):
            self.m_z = value
            self.__hash = hash((self.x,self.y,self.z))

    def asInts(self):
        return IntVector3(
            <long>self.x,
            <long>self.y,
            <long>self.z
        )

    def asFloats(self):
        return Vector3(
            <double>self.x,
            <double>self.y,
            <double>self.z
        )

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, index):
        if index in (0,"x"):
            return self.x
        elif index in (1,"y"):
            return self.y
        elif index in (2,"z"):
            return self.z
        else:
            raise IndexError("Unknown index for Vector2 object")

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1] and self.z == other[2]

    def __ne__(self, other):
        return self.x != other[0] or self.y != other[1] or self.z != other[2]

    @lru_cache(maxsize=1_000_000)
    def __add__(self, other):
        return Vector3(self.x + other[0], self.y + other[1], self.z + other[2])

    __radd__ = __add__

    @lru_cache(maxsize=1_000_000)
    def __sub__(self, other):
        return Vector3(self.x - other[0], self.y - other[1], self.z - other[2])

    @lru_cache(maxsize=1_000_000)
    def __rsub__(self, other):
        return Vector3(other[0] - self.x, other[1] - self.y, other[2] - self.z)

    @lru_cache(maxsize=1_000_000)
    def __mul__(self, other):
        return Vector3(self.x * other, self.y * other, self.z * other)

    __rmul__ = __mul__

    @lru_cache(maxsize=1_000_000)
    def __truediv__(self, other):
        return Vector3(self.x / other, self.y / other, self.z / other)

    def __rtruediv__(self, other):
        return Vector3(other / self.x, other / self.y, other / self.z)

    def __len__(self):
        return int(self.length())

    @lru_cache(maxsize=1_000_000)
    def length(self):
        return sqrt(self.x**2 + sqrt(self.y**2 + self.z**2))

    def __hash__(self) -> int:
        return self.__hash

    def __str__(self) -> str:
        return f"Vector3({self.x},{self.y},{self.z})"

    @lru_cache(maxsize=1_000_000)
    def dotProduct(self, other) -> float:
        return self.x * other[0] + self.y * other[1] + self.z * other[2]

    @lru_cache(maxsize=1_000_000)
    def crossProduct(self, other):
        return Vector3(self.y * other[2] - self.z * other[1], self.z * other[0] - self.x * other[2], self.x * other[1] - self.y * other[0])
    
    @lru_cache(maxsize=1_000_000)
    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @lru_cache(maxsize=1_000_000)
    def normalize(self):
        mag = self.magnitude()
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    cdef IntVector3 rotateX(self, Angle angle):
        rad = angle.rad
        cos_theta = cos(rad)
        sin_theta = sin(rad)
        y = self.y * cos_theta - self.z * sin_theta
        z = self.y * sin_theta + self.z * cos_theta
        return IntVector3(self.x, y, z)

    cdef IntVector3 rotateY(self, Angle angle):
        rad = angle.rad
        cos_theta = cos(rad)
        sin_theta = sin(rad)
        x = self.x * cos_theta + self.z * sin_theta
        z = -self.x * sin_theta + self.z * cos_theta
        return IntVector3(x, self.y, z)

    cdef IntVector3 rotateZ(self, Angle angle):
        rad = angle.rad
        cos_theta = cos(rad)
        sin_theta = sin(rad)
        x = self.x * cos_theta - self.y * sin_theta
        y = self.x * sin_theta
        return IntVector3(x, y, self.z)