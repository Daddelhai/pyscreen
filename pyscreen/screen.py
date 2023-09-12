import asyncio
from threading import RLock, Thread
from timeit import timeit
from enum import Enum

import pygame
from pygame.display import flip, set_caption, set_icon, set_mode
from pygame.locals import *
from pygame import Surface

from pyscreen.core.entity import Entity, Renderable

from pyscreen.eventHandler import EventHandler

from pyscreen.drawobj.util.renderstats import render_stats
from pyscreen.drawobj.util.loadingscreen import LoadingScreen
from .fps import ThreadingFPSCalculator

class UpscalingQuality(int, Enum):
    ULTRA = 8294400
    HIGH = 3686400
    MEDIUM = 2073600
    LOW = 1036800


class Screen(Thread):
    _is_open = False
    _show_debug = 0
    _entities: dict[int, Renderable] = {}
    _popups = {}
    _flags = None

    def __init__(self, eventHandler: EventHandler, width:int = 1250, height:int = 800, title="Window", 
                 icon = "icon.png", use_clear_screen: bool = False, resizeable: bool = True, titleframe: bool = True, 
                 use_double_buffer: bool = True, use_upscaling: bool = False, upscaling_quality:UpscalingQuality = UpscalingQuality.HIGH):
        self.eventHandler = eventHandler
        self.resizeable = resizeable
        self.titleframe = titleframe

        self.use_clear_screen = use_clear_screen
        self.use_double_buffer = use_double_buffer
        self._width = width
        self._height = height
        self.use_upscaling = use_upscaling
        self.upscaling_from = upscaling_quality.value

        self.title = title

        self.default_font = pygame.font.SysFont('arial',14)
        self.default_font_h1 = pygame.font.SysFont('arial',21,bold=True)
        self.default_font_h2 = pygame.font.SysFont('arial',18,bold=True)
        self.default_font_h3 = pygame.font.SysFont('arial',16,bold=True)
        self.default_font_bold = pygame.font.SysFont('arial',14,bold=True)
        self.default_font_italic = pygame.font.SysFont('arial',14,italic=True)
        self.default_font_bold_italic = pygame.font.SysFont('arial',14,bold=True,italic=True)

        try: 
            self.icon = pygame.image.load(icon)
        except FileNotFoundError:
            self.icon = None
        self.fps = ThreadingFPSCalculator()
        self._clock = pygame.time.Clock()

        self.motionlock = RLock()
        self.entitieslock = RLock()
        self.popupslock = RLock()
        
        self.render_stats = {}
        self._useMouseMoveEvent = False
        self._latestMouseMoveEvent = None
        self.surface = None
        

        self.loadingscreen: LoadingScreen|None = None

        super().__init__(name="RenderThread")
        self.start()

    @property
    def width(self) -> int:
        if self.surface is None:
            return self._width
        return self.surface.get_width()

    @property
    def height(self) -> int:
        if self.surface is None:
            return self._height
        return self.surface.get_height()

    
    @property
    def is_loading(self):
        if self.loadingscreen is None:
            return False
        return self.loadingscreen.is_loading

    @property
    def show_debug(self):
        return bool(self._show_debug)

    @property
    def entities(self):
        return self._entities

    @property
    def popups(self):
        return self._popups

    def add_entity(self, entity: Entity):
        with self.entitieslock:
            self._entities[entity.id] = entity

    def add_popup(self, entity: Entity):
        with self.popupslock:
            self._popups[entity.id] = entity

    def remove_entity(self, entity: Entity):
        with self.entitieslock:
            self._entities.pop(entity.id)

    def remove_popup(self, entity: Entity):
        with self.popupslock:
            self._popups.pop(entity.id)

    def get_event(self):
        if self._useMouseMoveEvent:
            tmp = self._latestMouseMoveEvent
            self._latestMouseMoveEvent = None
            self._useMouseMoveEvent = False
            return tmp
        

        if not self._events.empty():
            return self._events.get(False)
        return None

    def __del__(self):
        self.close()

    def close(self):
        self._is_open = False

    def wait_until_quit(self):
        self.join()

    def get_size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def iconify(self):
        assert self._is_open, "Cannot minimize closed window"
        pygame.display.iconify()

    def toggle_fullscreen(self):
        assert self._is_open, "Cannot toggle fullscreen of closed window"
        pygame.display.toggle_fullscreen()

    def run(self):
        self._is_open = True

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        flags = 0
        if self.resizeable:
            flags |= pygame.RESIZABLE
        if not self.titleframe:
            flags |= pygame.NOFRAME
        if self.use_double_buffer:
            flags |= pygame.DOUBLEBUF

        self._flags = flags

        self.window = set_mode((self.width, self.height), flags)
        if self.use_upscaling:
            window_p = self.window.get_width() * self.window.get_height()
            scale = window_p / self.upscaling_from
            if scale > 1:
                w = int(self.window.get_width() / scale)
                h = int(self.window.get_height() / scale)

                self.surface = Surface((w, h), 0, 32)
            else:
                self.surface = Surface((self.window.get_width(), self.window.get_height()), 0, 32)
        else:
            self.surface = self.window
        self.__last_window_size = (self.window.get_width(), self.window.get_height())

        
        set_caption(self.title)   
        if self.icon is not None:
            set_icon(self.icon)

        while self._is_open:
            for e in pygame.event.get():
                if self.use_upscaling:
                    if hasattr(e, "pos"):
                        x_scale = self.surface.get_width() / self.window.get_width()
                        y_scale = self.surface.get_height() / self.window.get_height()
                        e.pos = (int(e.pos[0] * x_scale), int(e.pos[1] * y_scale))

                if e.type == pygame.MOUSEMOTION:
                    self.eventHandler.enqueueMouseMotionEvent(e)
                elif e.type == pygame.QUIT:
                    self.eventHandler.enqueueEvent(e)
                    self.close()
                elif e.type != 772: #Ignore Unknown Event
                    self.eventHandler.enqueueEvent(e)
                

            self.fps()
            self._render()

    def _render(self):
            scale = 1
            if self.use_upscaling:
                if self.__last_window_size != (self.window.get_width(), self.window.get_height()):
                    window_p = self.window.get_width() * self.window.get_height()
                    scale = window_p / self.upscaling_from
                    if scale > 1:
                        w = int(self.window.get_width() / scale)
                        h = int(self.window.get_height() / scale)

                        self.surface = Surface((w, h), 0, 32)
                    else:
                        self.surface = Surface((self.window.get_width(), self.window.get_height()), 0, 32)
                    self.__last_window_size = (self.window.get_width(), self.window.get_height())
                    
            self._width, self._height = self.surface.get_size()

            self._clear_screen()

            if self.loadingscreen is not None and self.loadingscreen.is_loading:
                    self.loadingscreen.render(self.surface)
            else:
                if self.eventHandler is not None:
                    def f():
                        self.eventHandler.lock.acquire()
                    time = timeit(f, number=1)
                    self.render_stats["EventHandlerLock"] = {
                        "obj": None,
                        "time": time
                    }
                    self._print_entities()
                    self._print_popups()
                    self.eventHandler.lock.release() 
                else:
                    self._print_entities()
                    self._print_popups()

                self._print_hitboxes()
                self._print_fps()
                self._print_stats()

            if self.use_upscaling:
                if scale == 1:
                    pygame.transform.scale(
                        self.surface, 
                        (self.window.get_width(), self.window.get_height()),
                        self.window), 
                    (0, 0)
                else:
                    self.window.blit(self.surface, (0, 0))

            flip()

    def _print_entities(self):
        with self.entitieslock:
            for entity in self.entities.values():
                def f():
                    entity.render(self.surface)
                time = timeit(f, number=1)
                self.render_stats[entity.__class__.__name__] = {
                    "obj": entity,
                    "time": time
                }

    def _print_popups(self):
        with self.popupslock:
            for popup in self.popups.values():
                def f():
                    popup.render(self.surface)
                time = timeit(f, number=1)
                self.render_stats[popup.__class__.__name__] = {
                    "obj": popup,
                    "time": time
                }

    def _print_stats(self):
        if self._show_debug == 3:
            render_stats(self.surface, (10, 10), self.default_font, self)


    def _print_fps(self):
        if self._show_debug == 1:
            text_fps = self.default_font.render(f"fps: {self.fps}", True, (250,250,210))
            self.surface.blit(text_fps,(self.width - 90, 10))
        if self._show_debug == 2:
            text_fps = self.default_font.render(f"fps: {self.fps}", True, (250,250,210))
            self.surface.blit(text_fps,(self.width - 120, 10))
            text_fps = self.default_font.render(f"min: {int(self.fps.min())}", True, (250,250,210))
            self.surface.blit(text_fps,(self.width - 90, 30))
            text_fps = self.default_font.render(f"max: {int(self.fps.max())}", True, (250,250,210))
            self.surface.blit(text_fps,(self.width - 90, 50))
            text_fps = self.default_font.render(f"avg: {int(self.fps.avg())}", True, (250,250,210))
            self.surface.blit(text_fps,(self.width - 90, 70))

    def _print_hitboxes(self):
        if self._show_debug == 3:
            for entity in self.entities.values():
                if hasattr(entity, "printHitbox"):
                    entity.printHitbox(self.surface)
            

    def toggle_debug_view(self):
        if self._show_debug < 3:
            self._show_debug += 1
        elif self._show_debug == 3:
            self._show_debug = 0

    def _clear_screen(self):
        if self.use_clear_screen:
            self.surface.fill((0,0,0))