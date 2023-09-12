from datetime import datetime, timedelta
from time import sleep
from pyscreen.drawobj.util.background import BackgroundImage
from pyscreen.core.entity import StaticEntity

from pyscreen.drawobj.elements.box import Box
from pyscreen.drawobj.elements.flexbox import Flexbox
from pyscreen.drawobj.elements.label import Label
from pyscreen.drawobj.elements.progressbar import Progressbar
from threading import Thread
from pygame import Surface
from random import choice
from queue import Queue

from pyscreen.logging import getLogger
logger = getLogger()

class LoadingScreen(StaticEntity):
    def __init__(self, screen, 
                 tasks: list|None = None,
                 title: str = "Loading...", 
                 color: tuple[int, int, int] = (255, 255, 255),
                 tooltips: list[str] = None, 
                 tooltip_cycle_time: float = 5, 
                 show_action: bool = True,
                 background: tuple[int, int, int]|BackgroundImage = (20, 20, 50),
                 progress_color: tuple[int, int, int] = (0, 255, 0),
                 progress_background_color: tuple[int, int, int] = (0, 0, 0),
                 progress_width: float = .7,
                 progress_height: int = 20,
                 progress_border_radius: int = 5,
                 progress_border_color: tuple[int, int, int] = (255, 255, 255)):
        from pyscreen.screen import Screen
        self._screen: Screen = screen
        self._screen.loadingscreen = self

        self._is_loading = False
        self._loaded = False

        self._tasks_total = 0
        self._tasks_done = 0
        self._tasks = Queue()
        if tasks:
            for task in tasks:
                self._tasks.put(task)
                self._tasks_total += 1

        self._title = title
        self._color = color
        self._tooltips = tooltips if tooltips else []
        self._tooltip_cycle_time = tooltip_cycle_time
        self._next_tooltip_time = datetime.now()
        self._current_tooltip = ""
        self._current_action = ""
        self._show_action = show_action

        self._background = background
        self._progress_color = progress_color
        self._progress_background_color = progress_background_color
        self._progress_width = progress_width
        self._progress_height = progress_height
        self._progress_border_radius = progress_border_radius
        self._progress_border_color = progress_border_color
        
        self._tooltip_label = Label("", self._screen.eventHandler, font=self._screen.default_font_h3, color=self._color)
        self._action_label = Label("", self._screen.eventHandler, font=self._screen.default_font, color=self._color)
        self._title_label = Label(self._title, self._screen.eventHandler, font=self._screen.default_font_h1, color=self._color)
        self._progress_bar = Progressbar(self._screen.eventHandler, 0, color=self._progress_color, background=self._progress_background_color, border_color=self._progress_border_color, border_radius=self._progress_border_radius, height=self._progress_height)

        self._flexbox = Flexbox(screen, background=self._background, padding=(10, 10, 10, 10), gap=10)
        self._build()

        self.loading_thread = Thread(target=self._load, name="LoadingThread", daemon=True)
    

    @property
    def current_action(self):
        return self._current_action
    
    @current_action.setter
    def current_action(self, value):
        self._current_action = value
        self._action_label.value = value

    @property
    def current_tooltip(self):
        return self._current_tooltip
    
    @current_tooltip.setter
    def current_tooltip(self, value):
        self._current_tooltip = value
        self._tooltip_label.value = value

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        self._title = value
        self._title_label.value = value

    @property
    def progress(self):
        return self._progress_bar.value
    
    @progress.setter
    def progress(self, value):
        self._progress_bar.value = value


    def add_task(self, func):
        if self._is_loading:
            raise Exception("LoadingScreen is already loading")
        if self._loaded:
            raise Exception("LoadingScreen has already finished loading")
        
        self._tasks.put(func)
        self._tasks_total += 1

    def _build(self):
        # Title
        labelbox = Flexbox(self._flexbox, [self._title_label])
        self._flexbox.objects.append(labelbox)

        # Tooltip
        if self._tooltips:
            self._flexbox.objects.append(self._tooltip_label)

        # Progress
        assert self._progress_width > 0 and self._progress_width < 1
        p = (1 - self._progress_width) / 2
        progressbox = Box([self._progress_bar], padding=(0, p, 0, p), height=self._progress_height)
        self._flexbox.objects.append(progressbox)

        # Action
        if self._show_action:
            self._flexbox.objects.append(self._action_label)


    @property
    def is_loading(self):
        return not self._loaded

    def start(self):
        if self._is_loading:
            raise Exception("LoadingScreen is already loading")
        if self._loaded:
            raise Exception("LoadingScreen has already finished loading")
        self._is_loading = True
        self.loading_thread.start()

    def join(self):
        self.loading_thread.join()

    def reset(self, new_tasks: dict|None = None):
        self._tasks = Queue()
        self._tasks_done = 0
        self._tasks_total = 0

        if new_tasks:
            for task in new_tasks:
                self._tasks.put(task)
                self._tasks_total += 1

        self._is_loading = False
        self._loaded = False

        assert self.loading_thread.is_alive() == False
        self.loading_thread = Thread(target=self._load, name="LoadingThread", daemon=True)


    def _load(self):
        while not self._tasks.empty():
            task = self._tasks.get()
            task(self)
            self._tasks_done += 1
            self._progress_bar.value = self._tasks_done / self._tasks_total
            self.current_action = ""
        sleep(1)

        self._loaded = True
        self._is_loading = False

    def render(self, surface: Surface):
        if self._tooltips:
            if datetime.now() > self._next_tooltip_time:
                old_item = self._current_tooltip
                if len(self._tooltips) > 1:
                    while old_item == self._current_tooltip:
                        self._current_tooltip = choice(self._tooltips)
                else:
                    self._current_tooltip = self._tooltips[0]
                self._tooltip_label.value = self._current_tooltip
                self._next_tooltip_time = datetime.now() + timedelta(seconds=self._tooltip_cycle_time)


        self._flexbox.render(surface)

    def get_size(self) -> tuple[int,int]:
        return self._screen.get_size()
    
    def get_position(self) -> tuple[int,int]:
        return [0,0]