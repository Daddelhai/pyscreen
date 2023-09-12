from atc.core.distance cimport Distance
from pyscreen.gameobj.meteorology.airpressure import Pressure
from typing import Union

cdef class Altitude(Distance):
    def __init__(self, altitude: Union[int,float,Distance] = 0):
        if isinstance(altitude, Altitude):
            self._altitude = altitude._altitude
        elif isinstance(altitude, Distance):
            self._altitude = altitude._distance * 3.281
        else:
            self._altitude = altitude

    @property
    def _distance(self):
        return self._altitude / 3.281

    @classmethod
    def fromFL(cls, FL: int | float):
        return cls(FL * 100)

    @classmethod
    def fromFt(cls, ft: int | float, pressure: Pressure = None):
        if pressure is None:
            return cls(ft)
        return cls(ft - cls.__get_deviation(pressure))

    @staticmethod
    def __get_deviation(pressure: Pressure) -> float:
        return 145442.2 * (1 - (pressure.inHg / 29.92126) ** 0.190261)

    @property
    def ft(self):
        return self._altitude

    @property
    def FL(self):
        return self._altitude / 100

    def get_true_altitude(self, pressure: Pressure):
        return self._altitude + self.__get_deviation(pressure)
