class Angle:
    deg: float
    rad: float

    @classmethod
    def fromDeg(cls, deg: float):...
    def fromRad(cls, rad: float):...

    def __add__(self, other):...
    def __sub__(self, other):...

    def __eq__(self, other):...
    def __ne__(self, other):...
    def __lt__(self, other):...
    def __gt__(self, other):...
    def __le__(self, other):...
    def __ge__(self, other):...


    def __mul__(self, o: float):...
    def __rmul__(self, o: float):...
    def __truediv__(self, o: float):...


    def __float__(self):...
    def __int__(self):...
    def __neg__(self):...
    

    def __str__(self) -> str:...
    def __hash__(self) -> int:...