cdef class Coordinate:
    cdef double _longitude
    cdef double _latitude

    cdef Py_hash_t __hash_cache