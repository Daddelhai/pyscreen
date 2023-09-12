from copy import deepcopy
from functools import lru_cache
from math import degrees, radians
from libc.math cimport asin, atan2, cos, sin, sqrt, acos
from typing import Iterable, overload, Optional
import numpy as np

from .angle cimport Angle
from .distance cimport Distance
from .geomag.world_magnetic_model import WorldMagneticModel
from .vector cimport Vector2, Vector3, IntVector2, IntVector3, IVector2, IVector3


EARTH_RADIUS = Distance.EarthRadius()


cdef class Coordinate:
    def __init__(self, latitude:double = 0, longitude:double = 0):
        if latitude > 90 or latitude < -90:
            while latitude > 90 or latitude < -90:
                if latitude > 90:
                    latitude = 180 - latitude
                else:
                    latitude = -180 - latitude

                longitude += 180

        if longitude > 180 or longitude < -180:
            longitude = (longitude+540)%360-180

        self._latitude = latitude
        self._longitude = longitude

        self.__hash_cache = hash((self._longitude,self._longitude))

    @classmethod
    def fromStr(cls, latitude_str:str, longitude_str:str):
        latitude: double = 0
        longitude: double = 0

        for n, x in enumerate(latitude_str[:-1].split('-')):
            latitude += (float(x)) / 60 ** n

        for n, x in enumerate(longitude_str[:-1].split('-')):
            longitude += (float(x)) / 60 ** n

        if 'N' != latitude_str[-1]:
            latitude *= -1

        if 'E' != longitude_str[-1]:
            longitude *= -1

        return cls(latitude, longitude)

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: double):
        if latitude > 90 or latitude < -90:
            longitude = self._longitude

            while latitude > 90 or latitude < -90:
                if latitude > 90:
                    latitude = 180 - latitude
                else:
                    latitude = -180 - latitude

                longitude += 180

            self._latitude = latitude
            self._longitude = (longitude+540)%360-180

        else:
            self._latitude = latitude

        self.__hash_cache = hash((self._longitude,self._longitude))

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: double):
        if longitude > 180 or longitude < -180:
            self._longitude = (longitude+540)%360-180
        else:
            self._longitude = longitude

        self.__hash_cache = hash((self._longitude,self._longitude))
    

    @staticmethod
    @lru_cache(maxsize=1_000_000)
    def fromVector2(vector:IVector2, arg2, arg3 = None) -> Coordinate:
        return __c_FromVector2(vector, arg2, arg3)


    @staticmethod
    @lru_cache(maxsize=1_000_000)
    def fromVector3(vector:IVector3) -> Coordinate:
        lat = degrees(asin(-vector.y))
        lon = degrees(atan2(vector.x, vector.z))

        return Coordinate(lat,lon)

    def pbd(self, bearing: Angle, distance: Distance, is_magnetic: bool = True):
        return self.getPlaceByBearingDistance(bearing, distance, is_magnetic)

    @lru_cache(maxsize=10000)
    def getPlaceByBearingDistance(self, bearing: Angle, distance: Distance, is_magnetic: bool = True):
        return __c_GetPlaceByBearingDistance(self, bearing, distance, is_magnetic)

    @lru_cache(maxsize=1_000_000)
    def toVector2(self, gamemap) -> Vector2:
        return __c_ToVector2(self, gamemap)

    @lru_cache(maxsize=1_000_000)
    def toVector2IfVisible(self, gamemap) -> Vector2:
        return __c_ToVector2IfVisible(self, gamemap)


    
    @lru_cache(maxsize=1_000_000)
    def toVector3(self) -> Vector3:
        z = cos(radians(self.latitude)) * cos(radians(self.longitude))
        x = cos(radians(self.latitude)) * sin(radians(self.longitude))
        y = sin(radians(self.latitude))

        return Vector3(x, -y, z)

    @lru_cache(maxsize=1000)
    def _getInitialBearing(self, other):
        return __c_getInitialBearing(self, other)


    @lru_cache(maxsize=1000)
    def distance(self, other):
        return _c_distance(self, other)
    


    @lru_cache(maxsize=1000)
    def quj(self, other: Coordinate):
        return self._getInitialBearing(other)

    @lru_cache(maxsize=1000)
    def qte(self, other: Coordinate):
        return (other.quj(self))

    @lru_cache(maxsize=1000)
    def getMagneticDeclination(self) -> Angle:
        wmm = WorldMagneticModel()
        return  Angle.fromDeg(wmm.calc_mag_field(self.latitude, self.longitude).declination)

    @lru_cache(maxsize=1000)
    def getMagneticHeading(self, hdg: Angle) -> Angle:
        return hdg + self.getMagneticDeclination()

    @lru_cache(maxsize=1000)
    def qdm(self, other) -> Angle:
        quj = self.quj(other).deg
        if (quj > 0):
            return Angle.fromDeg(quj + self.getMagneticDeclination().deg)
        else:
            return Angle.fromDeg(quj - self.getMagneticDeclination().deg)

    @lru_cache(maxsize=1000)
    def qdr(self, other: Coordinate) -> Angle:
        return Angle.fromDeg(self.qdm(other).deg - 180)

    def __hash__(self) -> int:
        return self.__hash_cache

    def __eq__(self, other) -> bool:
        if isinstance(other, Coordinate):
            return self.longitude == other.longitude and self.latitude == other.latitude
        return hash(self) == hash(other)

    def copy(self):
        return deepcopy(Coordinate(self.latitude,self.longitude))

    @lru_cache(maxsize=1_000_000)
    def __add__(self, other):
        latitude = self.latitude + other.latitude
        longitude = self.longitude + other.longitude
        return Coordinate(latitude, longitude)

    __radd__ = __add__

    @lru_cache(maxsize=1_000_000)
    def __sub__(self, other):
        latitude = self.latitude - other.latitude
        longitude = self.longitude - other.longitude
        return Coordinate(latitude, longitude)

    __rsub__ = __sub__

    @lru_cache(maxsize=1_000_000)
    def __mul__(self, other: int):
        latitude = self.latitude * other
        longitude = self.longitude * other
        return Coordinate(latitude, longitude)

    __rmul__ = __mul__

    @lru_cache(maxsize=1_000_000)
    def __truediv__(self, other: int):
        latitude = self.latitude / other
        longitude = self.longitude / other
        return Coordinate(latitude, longitude)

    __rtruediv__ = __truediv__
    
    def serialize(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        }
    
    @classmethod
    def deserialize(cls, data):
        return cls(data["latitude"], data["longitude"])
    
    @property
    def angles(self):
        return Angle.fromDeg(self.latitude), Angle.fromDeg(self.longitude)



def _get_vectors_from_coordinates(mapcenter: Coordinate, *coordinates: Coordinate) -> Iterable[Vector3]:
    # Rotate the coordinate relative to the origin
    return ((coordinate - mapcenter).toVector3() for coordinate in coordinates)


def _get_coordinates_from_vectors(mapcenter: Coordinate, *vectors: Vector3) -> Iterable[Coordinate]:
    # Rotate the coordinate relative to the origin
    return (Coordinate.fromVector3(vector) + mapcenter for vector in vectors)


def coordinatesFromVectors(map, *vectors: Vector2) -> Iterable[Coordinate]:
    from pyscreen.drawobj.map import Map
    assert isinstance(map, Map)

    scale = map.scale
    center = map.center

    vector3s = []
    for vector in vectors:
        x = float(vector.x) / scale
        y = float(vector.y) / scale

        # len of vector (x,y,z) must be 1
        # calculate z
        z = sqrt(1 - x**2 - y**2)

        vector3 = Vector3(x,y,z)
        vector3s.append(vector3)

    coordinates = _get_coordinates_from_vectors(center, *vector3s)
    return coordinates


def vectorsFromCoordinates(map, *coordinates: Coordinate) -> Iterable[Vector2]:
    from pyscreen.drawobj.map import Map
    assert isinstance(map, Map)

    scale = map.scale
    center: Coordinate = map.center

    vector3s = _get_vectors_from_coordinates(center, *coordinates)

    vectors = []
    for vector3 in vector3s:
        x = vector3.x * scale
        y = vector3.y * scale

        vector2 = Vector2(x,y)
        vectors.append(vector2)

    return vectors









############
cdef Coordinate __c_FromVector2(IVector2 vector, arg2, arg3 = None):
    from pyscreen.drawobj.map import Map

    cdef double scale
    cdef Coordinate center

    if isinstance(arg2, Map):
        scale = float(arg2.scale)
        center = arg2.center

        offset = Vector2(arg2.width//2, arg2.height//2)
        vector = vector - offset
    else:
        scale = float(arg2)
        center = arg3

    x = (<double>vector.x) / scale
    y = (<double>vector.y) / scale

    # len of vector (x,y,z) must be 1
    # calculate z
    try:
        z = sqrt(1 - x**2 - y**2)
    except ValueError:
        z = 0
        # reduce x and y to have len 1
        x = x / sqrt(x**2 + y**2)
        y = y / sqrt(x**2 + y**2)

    vector3 = Vector3(x,y,z)

    return next(_get_coordinates_from_vectors(center, vector3))

cdef Coordinate __c_GetPlaceByBearingDistance(Coordinate self, Angle bearing, Distance distance, bint is_magnetic = True):
    cdef double R, brng, d, lat1, lon1, lat2, lon2

    R = EARTH_RADIUS.km
    
    brng = bearing.rad if is_magnetic else self.getMagneticHeading(bearing).rad
    d = distance.km

    lat1 = radians(self.latitude) #Current lat point converted to radians
    lon1 = radians(self.longitude) #Current long point converted to radians

    lat2 = asin( sin(lat1)*cos(d/R) +
        cos(lat1)*sin(d/R)*cos(brng))

    lon2 = lon1 + atan2(sin(brng)*sin(d/R)*cos(lat1),
                cos(d/R)-sin(lat1)*sin(lat2))

    lat2 = degrees(lat2)
    lon2 = degrees(lon2)
    
    return Coordinate(lat2,lon2)

cdef Vector2 __c_ToVector2(Coordinate self, gamemap):
    from pyscreen.drawobj.map import Map
    assert isinstance(gamemap, Map)

    vector = next(_get_vectors_from_coordinates(gamemap.center, self))

    # Z is not relevant
    v = Vector2(vector.x, vector.y)

    offset = Vector2(gamemap.width//2, gamemap.height//2)

    #apply scale
    v *= gamemap.scale
    v = v + offset
    return v

cdef Vector2 __c_ToVector2IfVisible(Coordinate self, gamemap):
    from pyscreen.drawobj.map import Map
    assert isinstance(gamemap, Map)

    vector = next(_get_vectors_from_coordinates(gamemap.center, self))

    # Z is not relevant
    if vector.z < 0:
        return None # not visible
    v = Vector2(vector.x, vector.y)

    offset = Vector2(gamemap.width//2, gamemap.height//2)

    #apply scale
    v *= gamemap.scale
    v = v + offset
    return v

cdef Angle __c_getInitialBearing(Coordinate self, Coordinate other):
    cdef double dLon, initX, initY, initBearing
    # Convert to radians
    other_lat = radians(other.latitude)
    self_lat = radians(self.latitude)
    other_lon = radians(other.longitude)
    self_lon = radians(self.longitude)

    # Calculate initial bearing
    dLon = other_lon - self_lon
    initX = cos(other_lat) * sin(dLon)
    initY = cos(self_lat) * sin(other_lat) - sin(self_lat) * cos(other_lat) * cos(dLon)
    initBearing = atan2(initX, initY)
    return Angle(initBearing)

cdef Distance _c_distance(Coordinate self, Coordinate other):
    # Distance with the Haversine formula
    R = EARTH_RADIUS.km
    dLat = radians(other.latitude - self.latitude)
    dLon = radians(other.longitude - self.longitude)
    a = sin(dLat / 2) * sin(dLat / 2) + cos(radians(self.latitude)) * cos(radians(other.latitude)) * sin(dLon / 2) * sin(dLon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c
    return Distance.fromKm(d)