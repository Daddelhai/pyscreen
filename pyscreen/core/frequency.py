
class Frequency:
    def __init__(self, freq:float, identifier=None):
        if isinstance(freq, int):
            self.int_freq = freq
        else:
            self.int_freq = int(freq * 1000)
        self.identifier = identifier

        if self.int_freq % 5 != 0:
            raise ValueError("invalid frequency")
        
        if self.int_freq > 2000_000 or self.int_freq < 100_000:
            raise ValueError("invalid frequency")
        
    def __str__(self) -> str:
        return str(self.int_freq / 1000.0)

    def __int__(self) -> int:
        return self.int_freq

    def __float__(self) -> float:
        return self.int_freq / 1000.0

    def __eq__(self, rhs) -> bool:
        return self.int_freq == rhs.int_freq

    def __ne__(self, rhs) -> bool:
        return self.int_freq != rhs.int_freq


    def __hash__(self) -> int:
        return hash(self.int_freq)
    
    def serialize(self):
        return {
            "int_freq": self.int_freq,
            "identifier": self.identifier
        }
    
    @classmethod
    def deserialize(cls, data):
        return cls(data["int_freq"], data["identifier"])