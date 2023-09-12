from threading import RLock
from timeit import timeit
from typing import Iterable

import pygame
from pygame.font import Font

from pyscreen.core.coordinate import Coordinate
from pyscreen.core.entity import DynamicEntity
from pyscreen.core.scale import Scale
from pyscreen.core.vector import Vector2
from pyscreen.hitbox import Hitbox
from pyscreen.screen import Screen

from .elements._util.margin import MarginInterface
from pyscreen.drawobj.base.renderable import Renderable
from pyscreen.settings import MAX_LATITUDE

class Map(Renderable, MarginInterface):
    def __init__(self, screen: Screen, center: Coordinate = Coordinate(0, 0), scale: Scale = Scale(10000), margin=(0,0,0,0), eventHandler=None, moveable=True):
        MarginInterface.__init__(self, screen, margin)

        self.backgroundColor = (0,0,45)

        self._scale = Scale(scale)
        self._entities = {0:[]}
        self.center = center
        self.lock = RLock()
        self.hash_lock = RLock()
        self.moveable = moveable

        self.render_stats = {}

        self.default_font: Font = screen.default_font

        self._screen = screen

        if eventHandler is not None:
            self._eventHandler = eventHandler
        elif screen.eventHandler is not None:
            self._eventHandler = screen.eventHandler
        else:
            raise AttributeError("You must provide an eventHandler")

        def onResize(e):
            self.resize()

        self._hitbox = Hitbox(self._eventHandler, Vector2(self.left, self.top), Vector2(self.get_size()), get_global_key_events=True, target=self)

        self._eventHandler.onResize = onResize
        self._hitbox.onScrollUp = self.scrollUp
        self._hitbox.onScrollDown = self.scrollDown

        self._hitbox.addEventListener("mouseDown", self.mouseDown, key=pygame.BUTTON_LEFT)
        self._hitbox.addEventListener("mouseUp", self.mouseUp, key=pygame.BUTTON_LEFT)

        self._hitbox.addEventListener("mouseMotion", self.mouseMove)
        self.mouseCenterPosition = None
        self.lastMouseCenterPosition = None
        self.movementSensitivity = 1

        self.mapDragged = False
        
        self.surface = pygame.Surface(self.get_size())

        with self.hash_lock:
            self.__hash_cache = None

    @property
    def screen(self):
        return self._screen

    def getEventHandler(self):
        return self._eventHandler

    def addEventListener(self, *args, **kwargs):
        return self._hitbox.addEventListener(*args, **kwargs)

    @property
    def scale(self):
        return self._scale

    @property
    def width(self):
        return self.surface.get_width()

    @property
    def height(self):
        return self.surface.get_height()


    def render(self, surface):
        self.surface.fill(self.backgroundColor)

        self.render_entities()

        if self._screen.show_debug:
            scale_print = self.default_font.render(f"Scale_factor: {self.scale.scale_factor}", True, (220,220,255))
            self.surface.blit(scale_print,(0,0))

            scale_print = self.default_font.render(f"Center Coordinates: Latitude: {self.center.latitude}, Longitude: {self.center.longitude}", True, (220,220,255))
            self.surface.blit(scale_print,(0,15))

            mouse_coord = Coordinate.fromVector2(self._eventHandler.mousePosition, self)
            scale_print = self.default_font.render(f"Mouse Coordinates: Latitude: {mouse_coord.latitude}, Longitude: {mouse_coord.longitude}", True, (220,220,255))
            self.surface.blit(scale_print,(0,30))

        surface.blit(self.surface, (self.left,self.top))

        self._hitbox.hitbox_location = Vector2(self.left,self.top)
        self._hitbox.hitbox_size = Vector2(self.get_size())

    def render_entities(self):
        def render_layer(entities: Iterable[DynamicEntity]):
            for entity in entities:
                def f():
                    entity.render(self)
                time = timeit(f,number=1)

                self.render_stats[entity.__class__.__name__] = {
                    "obj": entity,
                    "time": time
                }
        
        with self.lock:
            for entities in self._entities.values():
                render_layer(entities)
                

    def add_entity(self, *entities: DynamicEntity, z_index: int = 0):
        with self.lock:
            if z_index < 0:
                raise Exception("Z-Index must be positive")
            if z_index not in self._entities:
                self._entities[z_index] = [*entities]
                self._entities = dict(sorted(self._entities.items()))
                return

            for entity in entities:
                self._entities[z_index].append(entity)

    def resize(self, size:tuple|None=None):
        if size is None:
            size = self.get_size()

        self._hitbox.hitbox_size = Vector2(size)
        self._hitbox.hitbox_location = Vector2(self.left,self.top)
        self.surface = pygame.Surface(size)     

    def get_size(self):
        width = self._screen.width - self.left - self.right
        height = self._screen.height - self.top - self.bottom

        return (width, height)

    def scrollUp(self, e):
        if self.moveable:
            width, height = self.get_size()
            c_pos = Vector2(width / 2 + self.left, height / 2 + self.top)
            e_pos = Vector2(e.pos)

            deviation = (c_pos - e_pos) / 2
            dev_coord = self.__CoordinatefromVector2(deviation, scale=self.scale)

            self._scale = Scale( self._scale * 1.2 )

            self.center.longitude -= dev_coord.longitude
            self.center.latitude -= dev_coord.latitude

            with self.hash_lock:
                self.__hash_cache = None


    def scrollDown(self, e):
        if self.moveable:
            self._scale = Scale( self._scale / 1.2 )
            with self.hash_lock:
                self.__hash_cache = None

    def mouseDown(self, e):
        if self.moveable:
            self.mapDragged = True
            self.mouseCenterPosition = Vector2(e.pos)
            self.lastMouseCenterPosition = None

    def mouseUp(self, e):
        if self.moveable:
            self.mapDragged = False
            self.mouseCenterPosition = None
            self.lastMouseCenterPosition = None

    def mouseMove(self, e):
        if self.mapDragged:
            if self.lastMouseCenterPosition is None:
                self.lastMouseCenterPosition = Vector2(e.pos)

            e_pos = Vector2(e.pos)

            deviation = (self.lastMouseCenterPosition - e_pos) / self.movementSensitivity
            dev_coord = self.__CoordinatefromVector2(deviation, scale=self.scale)


            self.center.longitude += dev_coord.longitude
            self.center.latitude += dev_coord.latitude

            if self.center.latitude > MAX_LATITUDE:
                self.center.latitude = MAX_LATITUDE
            elif self.center.latitude < -MAX_LATITUDE:
                self.center.latitude = -MAX_LATITUDE

            self.lastMouseCenterPosition = e_pos

            with self.hash_lock:
                self.__hash_cache = None

    def __hash__(self) -> int:
        with self.hash_lock:
            if self.__hash_cache is None:
                self.__hash_cache = hash((self.scale, self.center))
            return int(self.__hash_cache)

    @staticmethod
    def __CoordinatefromVector2(vector:Vector2, center=None, scale: Scale = None):
        if scale is None:
            scale = 1

        if center is None:
            center = Coordinate(0,0)

        return Coordinate.fromVector2(vector, scale, center)