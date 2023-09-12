from atc.core.angle cimport Angle

cdef class IVector:
    pass

cdef class IVector2(IVector):
    pass
cdef class IVector3(IVector):
    pass

cdef class Vector2(IVector2):
    cdef double m_x, m_y
    cdef Py_hash_t __hash

cdef class Vector3(IVector3):
    cdef double m_x, m_y, m_z
    cdef Py_hash_t __hash

    cdef Vector3 rotateX(Vector3 self, Angle angle)
    cdef Vector3 rotateY(Vector3 self, Angle angle)
    cdef Vector3 rotateZ(Vector3 self, Angle angle)

cdef class IntVector2(IVector2):
    cdef long m_x, m_y
    cdef Py_hash_t __hash

cdef class IntVector3(IVector3):
    cdef long m_x, m_y, m_z
    cdef Py_hash_t __hash

    cdef IntVector3 rotateX(IntVector3 self, Angle angle)
    cdef IntVector3 rotateY(IntVector3 self, Angle angle)
    cdef IntVector3 rotateZ(IntVector3 self, Angle angle)