from pyscreen.drawobj.base.renderable import Renderable
from abc import abstractmethod
from pygame import Surface, Rect

class Entity(Renderable):
    @property
    @abstractmethod
    def changed(self):
        return True

class DynamicEntity(Entity):
    @property
    def changed(self):
        return True
    
    @changed.setter
    def changed(self, value):
        raise ValueError("DynamicEntity.changed can only be True")

class StaticEntity(Entity):
    @property
    @abstractmethod
    def changed(self):
        return True
    
    @abstractmethod
    def render(self, surface: Surface|None = None) -> Surface:
        raise NotImplementedError

    @abstractmethod
    def get_size(self) -> tuple[int,int]:
        raise NotImplementedError
    
    @abstractmethod
    def get_position(self) -> tuple[int,int]:
        raise NotImplementedError
    
    def get_rect(self) -> Rect:
        return Rect(self.get_position(), self.get_size())