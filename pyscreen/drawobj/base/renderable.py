import abc

import pygame


class Renderable:
    __object_id = None
    _changed = True

    @property
    def id(self):
        if self.__object_id is None:
            self.__object_id = id(self)
        return self.__object_id
        
    @abc.abstractmethod
    def render(self, surface: pygame.Surface):
        pass


    @property
    def changed(self):
        return self._changed

    @changed.setter
    def changed(self, value):
        self._changed = value