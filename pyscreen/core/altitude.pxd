from atc.core.distance cimport Distance

cdef class Altitude(Distance):
    cdef double _altitude