class Distance:
    @classmethod
    def fromKm(cls, distance: float):...

    @classmethod
    def fromCm(cls, distance: float):...

    @classmethod
    def fromDm(cls, distance: float):...

    @classmethod
    def fromMm(cls, distance: float):...

    @classmethod
    def fromM(cls, distance: float):...

    @classmethod
    def fromNM(cls, distance: float):...
    
    @property
    def km(self):...

    @property
    def cm(self):...

    @property
    def dm(self):...

    @property
    def mm(self):...

    @property
    def m(self):...

    @property
    def nm(self):...


    @staticmethod
    def EarthRadius() -> Distance:
        return Distance.fromKm(6371.009)

    @staticmethod
    def EarthCircumference() -> Distance:
        return Distance.fromKm(40075.017)

    @staticmethod
    def EarthDiameter() -> Distance:
        return Distance.fromKm(12742.018)