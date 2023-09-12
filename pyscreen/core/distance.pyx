cdef class Distance:
    def __init__(self, distance: double = 0):
        self._distance = distance


    @classmethod
    def fromKm(cls, distance: double):
        return cls(distance*1000)

    @classmethod
    def fromCm(cls, distance: double):
        return cls(distance/100)

    @classmethod
    def fromDm(cls, distance: double):
        return cls(distance/10)

    @classmethod
    def fromMm(cls, distance: double):
        return cls(distance/1000)

    @classmethod
    def fromM(cls, distance: double):
        return cls(distance)

    @classmethod
    def fromNM(cls, distance: double):
        return cls(distance*1852)



    property km:
        def __get__(self: Distance):
            return self._distance/1000
            
        def __set__(self: Distance, distance: double):
            self._distance = distance*1000


    property cm:
        def __get__(self: Distance):
            return self._distance*100
            
        def __set__(self: Distance, distance: double):
            self._distance = distance/100

    property dm:
        def __get__(self: Distance):
            return self._distance*10
            
        def __set__(self: Distance, distance: double):
            self._distance = distance/10

    property mm:
        def __get__(self: Distance):
            return self._distance*1000
            
        def __set__(self: Distance, distance: double):
            self._distance = distance/1000

    property m:
        def __get__(self: Distance):
            return self._distance
            
        def __set__(self: Distance, distance: double):
            self._distance = distance

    property NM:
        def __get__(self: Distance):
            return self._distance/1852
            
        def __set__(self: Distance, distance: double):
            self._distance = distance*1852




    def __eq__(self: Distance, o: Distance):
        return self.m == o.m

    def __ne__(self: Distance, o: Distance):
        return self.m != o.m

    def __lt__(self: Distance, o: Distance):
        return self.m < o.m

    def __gt__(self: Distance, o: Distance):
        return self.m > o.m

    def __le__(self: Distance, o: Distance):
        return self.m <= o.m

    def __ge__(self: Distance, o: Distance):
        return self.m >= o.m




    def __add__(self: Distance, o: Distance):
        return Distance(self.m + o.m)

    def __sub__(self: Distance, o: Distance):
        return Distance(self.m - o.m)

    def __radd__(self: Distance, o: Distance):
        return Distance(self.m + o.m)

    def __rsub__(self: Distance, o: Distance):
        return Distance(self.m - o.m)

    def __mul__(self: Distance, o: double):
        return Distance(self.m * o)

    def __rmul__(self: Distance, o: double):
        return Distance(self.m * o)

    def __truediv__(self: Distance, o: double):
        return Distance(self.m / o)

    def __rtruediv__(self: Distance, o: double):
        return Distance(self.m / o)

    def __floordiv__(self: Distance, o: double):
        return Distance(self.m // o)

    def __rfloordiv__(self: Distance, o: double):
        return Distance(self.m // o)

    def __neg__(self: Distance):
        return Distance(-self.m)

    def abs(self: Distance):
        return Distance(abs(self.m))

    def __hash__(self) -> int:
        return hash(self.m)
    
    @staticmethod
    def EarthRadius() -> Distance:
        return Distance.fromKm(6371.009)

    @staticmethod
    def EarthCircumference() -> Distance:
        return Distance.fromKm(40075.017)

    @staticmethod
    def EarthDiameter() -> Distance:
        return Distance.fromKm(12742.018)
