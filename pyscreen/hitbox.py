import inspect
from types import NoneType
from pyscreen.core.vector import Vector2, IVector2
from .eventHandler import EventHandler, EventListenerFuture

from pyscreen.logging import getLogger
logger = getLogger()

class FocusEvent(object):
    def __init__(self, state):
        self.state = state

class ChangeEvent(object):
    ...

class _Void:
    ...

class HoverStateEvent(object):
    def __init__(self, state):
        self.state = state

class Hitbox:
    def __init__(self, eventHandler: EventHandler, location: Vector2|None = None, size: Vector2|None = None, get_global_key_events:bool=False, target=None):
        self._hitbox_location = Vector2(location) if location is not None else Vector2(0,0)
        self._hitbox_size = Vector2(size) if size is not None else Vector2(0,0)
        self.get_global_key_events = get_global_key_events
        self.target = target

        self.async_tasks = []
        
        self.hasFocus = False
        self.value_func = None
        self.start_value = _Void
        self._mouse_was_in_hitbox = False

        self.__mouseMotionListenerAdded = False
        self.__mouseDownListenerAdded = False
        self.__forceReleaseListenerAdded = False

        self.enabled = True

        self.eventListeners = {
            "mouseEnter": [],
            "mouseLeave": [],
            "focus": [],
            "focusRelease": [],
            "change": []
        }

        self.__eventHandler: EventHandler = eventHandler
        self.__globalEventListeners = []

    def destruct(self):
        if self.hasFocus:
            self.forceReleaseFocus()

        for e in self.__globalEventListeners:
            self.__eventHandler.removeEventListener(e)

        self.__mouseMotionListenerAdded = False
        self.__mouseDownListenerAdded = False
        self.__forceReleaseListenerAdded = False

        self._hitbox_location =  Vector2(0,0)
        self._hitbox_size = Vector2(0,0)

        self.enabled = False

    @property
    def hitbox_location(self):
        return self._hitbox_location

    @property
    def hitbox_size(self):
        return self._hitbox_size

    @hitbox_location.setter
    def hitbox_location(self, value):
        if not isinstance(value, IVector2):
            value = Vector2(value)
        self._hitbox_location = value

    @hitbox_size.setter
    def hitbox_size(self, value):
        if not isinstance(value, IVector2):
            value = Vector2(value)
        self._hitbox_size = value

    @property
    def outer(self):
        return self.__eventHandler

    def __del__(self):
        for listener in self.__globalEventListeners:
            self.__eventHandler.removeEventListener(listener)

    async def __exec(self, f, e):
        r = None
        ex = None

        params = inspect.signature(f).parameters
        if inspect.iscoroutinefunction(f):
            try:
                if len(params) == 1:
                    r = await f(e)
                else:
                    r = await f()
            except Exception as exc:
                ex = exc
        else:
            try:
                if len(params) == 1:
                    r = f(e)
                else:
                    r = f()
            except Exception as exc:
                ex = exc

        f.futureWrapper.result = r
        f.futureWrapper.exception = ex

        return True

    def __setattr__(self, name, value):
        if name.startswith('on'):
            self.addEventListener(name[2].lower()+name[3:],value)
        else: 
            super().__setattr__(name, value)

    def _mouse_in_hitbox(self, x, y):
        if x < self.hitbox_location.x or x > self.hitbox_location.x + self.hitbox_size.x:
            return False
        if y < self.hitbox_location.y or y > self.hitbox_location.y + self.hitbox_size.y:
            return False
        return True


    async def _onMouseMotion(self, event):
        if not self.enabled:
            return
        await self._onMouseEnter(event)
        await self._onMouseLeave(event)
        self.__lastMousePosition = event.pos

    async def _onMouseDown(self, event):
        if not self.enabled:
            return
        if self.hasFocus:
            if not self._mouse_in_hitbox(*event.pos):
                await self.releaseFocus()


    async def _onMouseEnter(self, event, force = False):
        if not self.enabled:
            return
        event.target = self.target
        if force or (self._mouse_in_hitbox(*event.pos) != self._mouse_was_in_hitbox):
            self._mouse_was_in_hitbox = True
            self.eventListeners["mouseEnter"] = [listener for listener in self.eventListeners["mouseEnter"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]

    async def _onMouseLeave(self, event, force = False):
        if not self.enabled:
            return
        event.target = self.target
        if force or (self._mouse_in_hitbox(*event.pos) != self._mouse_was_in_hitbox):
            self._mouse_was_in_hitbox = False
            self.eventListeners["mouseLeave"] = [listener for listener in self.eventListeners["mouseLeave"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]

    async def _onFocus(self, event = None, value_f = None):
        if not self.enabled:
            return
        if event is None:
            event = FocusEvent(True)
        event.target = self.target

        if value_f is not None:
            self.start_value = value_f()
            self.value_func = value_f

        self.eventListeners["focus"] = [listener for listener in self.eventListeners["focus"] 
            if await self.__exec(listener,event) and not listener.callonce
        ]

    async def _onFocusRelease(self, event = None):
        if not self.enabled:
            return
        if event is None:
            event = FocusEvent(False)
        event.target = self.target

        if self.value_func is not None:
            if self.start_value != self.value_func():
                await self._onChange(event)
            self.start_value = _Void
        self.value_func = None

        self.eventListeners["focusRelease"] = [listener for listener in self.eventListeners["focusRelease"] 
            if await self.__exec(listener,event) and not listener.callonce
        ]

    async def _onChange(self, event):
        if not self.enabled:
            return
        self.eventListeners["change"] = [listener for listener in self.eventListeners["change"] 
            if await self.__exec(listener,event) and not listener.callonce
        ]

    def trigger_onchange(self):
        async def wrapper():
            event = ChangeEvent()
            event.target = self.target
            await self._onChange(event)
        self.__eventHandler.queueTask(wrapper)
        

    async def focus(self, value_f = None):
        if not self.__mouseDownListenerAdded:
            self.__globalEventListeners.append(
                self.__eventHandler.addEventListener("mouseDown", self._onMouseDown)
            )
        if not self.__forceReleaseListenerAdded:
            self.__globalEventListeners.append(
                self.__eventHandler.addEventListener("close", self.forceReleaseFocus)
            )

        self.hasFocus = True
        await self._onFocus(None, value_f)
        self.__eventHandler.setFocus(self)

    async def manual_focus(self, value_f = None):
        if not self.__forceReleaseListenerAdded:
            self.__globalEventListeners.append(
                self.__eventHandler.addEventListener("close", self.forceReleaseFocus)
            )

        self.hasFocus = True
        await self._onFocus(None, value_f)
        self.__eventHandler.setFocus(self)

    async def releaseFocus(self):
        await self._onFocusRelease(None)
        self.__eventHandler.releaseFocus(self)
        self.hasFocus = False

    def forceReleaseFocus(self):
        self.__eventHandler.releaseFocus(self)
        self.hasFocus = False


    def addEventListener(self, eventtype, func, once=False, key=None, key_mods:list|None=None, override:bool=False):
        if eventtype not in self.eventListeners:
            if not inspect.iscoroutinefunction(func):
                def wrapper(event):
                    if not self.enabled:
                        return
                    if self._mouse_in_hitbox(*event.pos):
                        event.target = self.target
                        if hasattr(event,"pos"):
                            event.relpos = (
                                event.pos[0] - self.hitbox_location.x,
                                event.pos[1] - self.hitbox_location.y
                            )

                        params = inspect.signature(func).parameters
                        if len(params) == 1:
                            func(event)
                        else:
                            func()

            else:
                async def wrapper(event):
                    if not self.enabled:
                        return
                    if self._mouse_in_hitbox(*event.pos):
                        event.target = self.target
                        if hasattr(event,"pos"):
                            event.relpos = (
                                event.pos[0] - self.hitbox_location.x,
                                event.pos[1] - self.hitbox_location.y
                            )

                        params = inspect.signature(func).parameters
                        if len(params) == 1:
                            await func(event)
                        else:
                            await func()

            l = self.addGlobalEventListener(eventtype, wrapper, once, key, key_mods, override)
            self.__globalEventListeners.append(l)
            return l
        
        if eventtype in ["mouseEnter", "mouseLeave"] and not self.__mouseMotionListenerAdded:
            self.__globalEventListeners.append(
                self.__eventHandler.addEventListener("mouseMotion", self._onMouseMotion)
            )
            self.__mouseMotionListenerAdded = True
        
        if not inspect.iscoroutinefunction(func):
            def eventListener(e):
                params = inspect.signature(func).parameters
                if len(params) == 1:
                    func(e)
                else:
                    func()
        else:
            async def eventListener(e):
                params = inspect.signature(func).parameters
                if len(params) == 1:
                    await func(e)
                else:
                    await func()

        eventListener.callonce = once
        eventListener.key = key
        eventListener.key_mods = key_mods
        eventListener.futureWrapper = EventListenerFuture(eventListener, eventtype)

        self.eventListeners[eventtype].append(eventListener)

        return eventListener.futureWrapper

    def addGlobalEventListener(self, eventtype, func, once=False, key=None, key_mods:list|None=None, override:bool=False):
        return self.__eventHandler.addEventListener(eventtype, func, once, key, key_mods, override)

    def removeEventListener(self, eventListenerFuture: EventListenerFuture):
        if eventListenerFuture.eventtype in self.eventListeners:
            len_before = len(self.eventListeners[eventListenerFuture.eventtype])
            self.eventListeners[eventListenerFuture.eventtype] = [listener for listener in self.eventListeners[eventListenerFuture.eventtype] if id(listener) != eventListenerFuture.id ]
            return len_before - len(self.eventListeners[eventListenerFuture.eventtype])
        else:
            return self.__eventHandler.removeEventListener(eventListenerFuture)