from abc import abstractmethod
from typing import Protocol, runtime_checkable, TypeVar

N = TypeVar("N", int, float, covariant=True)

@runtime_checkable
class SupportsSize(Protocol[N]):
    @property
    @abstractmethod
    def height(self) -> N:
        pass

    @property
    @abstractmethod
    def width(self) -> N:
        pass


