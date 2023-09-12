from abc import abstractmethod
from queue import PriorityQueue, Queue
from threading import Thread
from pyscreen.core.lock import AsyncRLock
import threading


from pyscreen.core.vector import Vector2
import inspect
import asyncio
import pygame
from typing import Callable
import datetime
import copy
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from pyscreen.logging import getLogger
logger = getLogger()

class EventListenerFuture:
    def __init__(self, func: Callable, type):
        self.func = func
        self.result = None
        self.exception = None
        self.eventtype = type

    @property
    def id(self):
        return id(self.func)


class FocusChange(Exception):...
class FocusError(TypeError):...
class TickEvent(object):
    def __init__(self, tick):
        self.tick = tick


class IntervalEvent(object):
    def __init__(self, func, interval):
        self.func = func
        self.interval = interval
        self.last = datetime.datetime.now()

    async def __call__(self):
        if datetime.datetime.now() - self.last >= self.interval:
            self.last = datetime.datetime.now()
            if inspect.iscoroutinefunction(self.func):
                await self.func()
            else:
                self.func()
    
    @property
    def id(self):
        return id(self)
    
    def __eq__(self, other):
        return self.id == other.id
    


class EventHandler(Thread):
    obj_has_focus = False
    _focus_objid = None

    mousePosition = Vector2(0,0)
    _tick = 0

    _intervalEvents = {}

    _mouseMotionEvent = None
    _events = Queue(100)
    _eventListeners = {
        "close": [],
        "resize": [],
        "keyDown": [],
        "keyUp": [],
        "scrollDown": [],
        "scrollUp": [],
        "mouseDown": [],
        "mouseUp": [],
        "mouseMotion": [],
        "mouseClick": [],
        "mouseDoubleClick": [],
        "fileDrop": [],
        "textDrop": [],
        "drag": [],
        "drop": [],
        "tick": [],
    }
    _focusEventListeners = {
        "close": [],
        "resize": [],
        "keyDown": [],
        "keyUp": [],
        "scrollDown": [],
        "scrollUp": [],
        "mouseDown": [],
        "mouseUp": [],
        "mouseMotion": [],
        "mouseClick": [],
        "mouseDoubleClick": [],
        "fileDrop": [],
        "textDrop": [],
        "drag": [],
        "drop": [],
        "tick": [],
    }
    _running = True

    lshift_active = False
    rshift_active = False
    lctrl_active = False
    rctrl_active = False
    lalt_active = False
    ralt_active = False

    @property
    def shift_active(self):
        return self.lshift_active or self.rshift_active
    @property
    def ctrl_active(self):
        return self.lctrl_active or self.rctrl_active
    @property
    def alt_active(self):
        return self.lalt_active or self.ralt_active

    @property
    def tick(self):
        return self._tick

    def __init__(self):
        self.__update_event_listeners()
        self.skipped_mouse_motion_events = 0
        self.last_mouse_motion_event = None
        self.lock = AsyncRLock()
        self._last_mouse_down_event = datetime.datetime.now()
        self._last_mouse_click_event = datetime.datetime.now()
        self._last_mouse_click_event_pos = (0,0)
        super().__init__(name="EventHandler")
        self.tasks = Queue()
        self.running_tasks = set()
        self.start()

    def __setattr__(self, name, value):
        if name.startswith('on'):
            self.addEventListener(name[2].lower()+name[3:],value)
        else: 
            super().__setattr__(name, value)

    def enqueueEvent(self, e):
        self._events.put(e)

    def enqueueMouseMotionEvent(self, e):
        self._mouseMotionEvent = e

    def getEvent(self, check_mouse_motion=False):
        if check_mouse_motion and self._mouseMotionEvent is not None:
            event = self._mouseMotionEvent
            self._mouseMotionEvent = None
            return event
        if not self._events.empty():
            return self._events.get()

    async def run_tasks(self):
        while not self.tasks.empty():
            func, args = self.tasks.get()
            try:
                if inspect.iscoroutinefunction(func):
                    if args is None:
                        self.running_tasks.add( asyncio.create_task(func()) )
                    else:
                        self.running_tasks.add( asyncio.create_task(func(*args)) )
                else:
                    if args is None:
                        func()
                    else:
                        func(*args)
            except Exception as e:
                logger.exception(e)

        if self.running_tasks:
            done, unfinished = await asyncio.wait(self.running_tasks, timeout=0.1, return_when=asyncio.ALL_COMPLETED)
            self.running_tasks = unfinished

    def run(self):
        self.aioloop = asyncio.new_event_loop()
        self.threadid = threading.get_ident()
        asyncio.set_event_loop(self.aioloop)
        asyncio.run(self.arun())

    async def arun(self):
        while self._running:
            event = self.getEvent(True)
            with self.lock:
                while event is not None:
                    try:
                        self.__update_event_listeners()
                        # if self.last_mouse_motion_event is not None:
                        #     if event.type != pygame.MOUSEMOTION:
                        #         await self._onMouseMotion(self.last_mouse_motion_event)
                        #     else:
                        #         self.skipped_mouse_motion_events += 1
                        #         if self.skipped_mouse_motion_events > 5:
                        #             await self._onMouseMotion(self.last_mouse_motion_event)

                        if event.type == pygame.QUIT:
                            await self._onClose(event)
                            break

                        
                        elif event.type == pygame.WINDOWRESIZED:
                            await self._onResize(event)

                        elif event.type == pygame.MOUSEMOTION:
                            self.mousePosition = Vector2(event.pos)
                            await self._onMouseMotion(event)
                            #self.last_mouse_motion_event = event
                            

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == pygame.BUTTON_WHEELUP:
                                await self._onScrollUp(event)
                            elif event.button == pygame.BUTTON_WHEELDOWN:
                                await self._onScrollDown(event)
                            elif event.button == pygame.BUTTON_LEFT:
                                self._last_mouse_down_event = datetime.datetime.now()
                            await self._onMouseDown(event)
                        elif event.type == pygame.WINDOWRESIZED:
                            await self._onResize(event)
                        elif event.type == pygame.MOUSEBUTTONUP:
                            if event.button == pygame.BUTTON_LEFT:
                                if (datetime.datetime.now() - self._last_mouse_down_event).microseconds <= 250000:
                                    if (datetime.datetime.now() - self._last_mouse_click_event).microseconds <= 250000:
                                        if (event.pos[0] - self._last_mouse_click_event_pos[0])**2 + (event.pos[1] - self._last_mouse_click_event_pos[1])**2 <= 50:
                                            # max 7 pixel distance between mouse down and mouse up -> (5*5) + (5*5) = 50 -> sqrt(50) = 7.07 (max distance)
                                            await self._onMouseDoubleClick(event)
                                            self._last_mouse_click_event = datetime.datetime(1970,1,1)
                                        else:
                                            await self._onMouseClick(event)
                                            self._last_mouse_click_event = datetime.datetime.now()
                                            self._last_mouse_click_event_pos = event.pos
                                    else:
                                        await self._onMouseClick(event)
                                        self._last_mouse_click_event = datetime.datetime.now()
                                        self._last_mouse_click_event_pos = event.pos
                            await self._onMouseUp(event)

                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.KMOD_LSHIFT:
                                self.lshift_active = True
                            elif event.key == pygame.KMOD_RSHIFT:
                                self.rshift_active = True
                            elif event.key == pygame.KMOD_LCTRL:
                                self.lctrl_active = True
                            elif event.key == pygame.KMOD_RCTRL:
                                self.rctrl_active = True
                            elif event.key == pygame.KMOD_LALT:
                                self.lalt_active = True
                            elif event.key == pygame.KMOD_RALT:
                                self.ralt_active = True

                            await self._onKeyDown(event)

                        elif event.type == pygame.KEYUP:
                            if event.key == pygame.KMOD_LSHIFT:
                                self.lshift_active = False
                            elif event.key == pygame.KMOD_RSHIFT:
                                self.rshift_active = False
                            elif event.key == pygame.KMOD_LCTRL:
                                self.lctrl_active = False
                            elif event.key == pygame.KMOD_RCTRL:
                                self.rctrl_active = False
                            elif event.key == pygame.KMOD_LALT:
                                self.lalt_active = False
                            elif event.key == pygame.KMOD_RALT:
                                self.ralt_active = False

                            await self._onKeyUp(event)

                        elif event.type == pygame.DROPFILE:
                            await self._onFileDrop(event)

                        elif event.type == pygame.DROPTEXT:
                            await self._onTextDrop(event)

                        elif event.type == pygame.DROPBEGIN:
                            await self._onDrag(event)

                        elif event.type == pygame.DROPCOMPLETE:
                            await self._onDrop(event)

                    
                    except Exception as e:
                        logger.exception(e)
                    event = self.getEvent()

                await self.run_tasks()
                await self._onTick()
                await self.run_interval_events()


    async def run_interval_events(self):
        tasks = []
        for event in self._intervalEvents.values():
            tasks.append(asyncio.create_task(event()))
        await asyncio.gather(*tasks)
                    

    async def __exec(self, f, e):
        r = None
        ex = None

        e.globals = EventGlobals(self)


        try:
            if inspect.iscoroutinefunction(f):
                r = asyncio.create_task( f(e) )
                self.running_tasks.add(r)
            else:
                r = f(e)
        except Exception as exc:
            ex = exc

        
        if ex is not None:
            logger.warn("Exception raised in '%s' event: %s", f.futureWrapper.eventtype, ex)

        f.futureWrapper.result = r
        f.futureWrapper.exception = ex

        #if old_focus != self.focus_obj:
        #    raise FocusChange()
        
        return True


    async def _onTick(self):
        event = TickEvent(self._tick)
        self._tick += 1
        event.pos = self.mousePosition 

        if self.focusEventListeners["tick"]:
            self.focusEventListeners["tick"] = [listener for listener in self.focusEventListeners["tick"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]
        else:
            self.eventListeners["tick"] = [listener for listener in self.eventListeners["tick"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]

    async def _onFileDrop(self, event):
        if not hasattr(event, "pos"):
            event.pos = self.mousePosition 
        if self.focusEventListeners["fileDrop"]:
            self.focusEventListeners["fileDrop"] = [listener for listener in self.focusEventListeners["fileDrop"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]
        else:
            self.eventListeners["fileDrop"] = [listener for listener in self.eventListeners["fileDrop"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]

    async def _onDrag(self, event):
        if not hasattr(event, "pos"):
            event.pos = self.mousePosition 
        if self.focusEventListeners["drag"]:
            self.focusEventListeners["drag"] = [listener for listener in self.focusEventListeners["drag"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]
        else:
            self.eventListeners["drag"] = [listener for listener in self.eventListeners["drag"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]

    async def _onDrop(self, event):
        if not hasattr(event, "pos"):
            event.pos = self.mousePosition 
        if self.focusEventListeners["drop"]:
            self.focusEventListeners["drop"] = [listener for listener in self.focusEventListeners["drop"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]
        else:
            self.eventListeners["drop"] = [listener for listener in self.eventListeners["drop"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]

    async def _onTextDrop(self, event):
        if not hasattr(event, "pos"):
            event.pos = self.mousePosition 
        if self.focusEventListeners["textDrop"]:
            self.focusEventListeners["textDrop"] = [listener for listener in self.focusEventListeners["textDrop"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]
        else:
            self.eventListeners["textDrop"] = [listener for listener in self.eventListeners["textDrop"] 
                if await self.__exec(listener,event) and not listener.callonce
            ]

    async def _onClose(self, event):
        if self.obj_has_focus:
            skip = False
            try:
                if self.focusEventListeners["close"]:
                    for listener in self.focusEventListeners["close"]:
                        await self.__exec(listener,event)
                else:
                    skip = True
                    for listener in self.eventListeners["close"]:
                        await self.__exec(listener,event)
            except FocusChange:
                if not skip:
                    for listener in self.eventListeners["close"]:
                        await self.__exec(listener,event)
            if self.obj_has_focus:
                raise Exception("Focus was not released on close event!")
        else:
            for listener in self.eventListeners["close"]:
                await self.__exec(listener,event)

        self._running = False


    async def _onMouseMotion(self, event):
        self.last_mouse_motion_event = None
        self.skipped_mouse_motion_events = 0 

        if self.focusEventListeners["mouseMotion"]:
            for listener in self.focusEventListeners["mouseMotion"]:
                await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["mouseMotion"]:
                await self.__exec(listener,event)

    async def _onResize(self, event):
        if self.focusEventListeners["resize"]:
            for listener in self.focusEventListeners["resize"]:
                await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["resize"]:
                await self.__exec(listener,event)

    async def _onMouseClick(self, event):
        if self.focusEventListeners["mouseClick"]:
            for listener in self.focusEventListeners["mouseClick"]:
                await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["mouseClick"]:
                await self.__exec(listener,event)

    async def _onMouseDoubleClick(self, event):
        if self.focusEventListeners["mouseDoubleClick"]:
            for listener in self.focusEventListeners["mouseDoubleClick"]:
                await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["mouseDoubleClick"]:
                await self.__exec(listener,event)

    async def _onScrollDown(self, event):
        if self.focusEventListeners["scrollDown"]:
            for listener in self.focusEventListeners["scrollDown"]:
                await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["scrollDown"]:
                await self.__exec(listener,event)

    async def _onScrollUp(self, event):   
        if self.focusEventListeners["scrollUp"]:
            for listener in self.focusEventListeners["scrollUp"]:
                await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["scrollUp"]:
                await self.__exec(listener,event)

    async def _onKeyDown(self, event):
        if self.focusEventListeners["keyDown"]:
            for listener in self.focusEventListeners["keyDown"]:
                if self._keycheck(listener, event):
                    await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["keyDown"]:
                if self._keycheck(listener, event):
                    await self.__exec(listener,event)

    async def _onKeyUp(self, event):
        if self.focusEventListeners["keyUp"]:
            for listener in self.focusEventListeners["keyUp"]:
                if self._keycheck(listener, event):
                    await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["keyUp"]:
                if self._keycheck(listener, event):
                    await self.__exec(listener,event)

    async def _onMouseDown(self, event):
        if self.focusEventListeners["mouseDown"]:
            for listener in self.focusEventListeners["mouseDown"]:
                if self._buttoncheck(listener, event):
                    await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["mouseDown"]:
                if self._buttoncheck(listener, event):
                    await self.__exec(listener,event)

    async def _onMouseUp(self, event):
        if self.focusEventListeners["mouseUp"]:
            for listener in self.focusEventListeners["mouseUp"]:
                if self._buttoncheck(listener, event):
                    await self.__exec(listener,event)
        else:
            for listener in self.eventListeners["mouseUp"]:
                if self._buttoncheck(listener, event):
                    await self.__exec(listener,event)

    def _keycheck(self, listener, event):
        if listener.key is None:
            return True
        if listener.key != event.key:
            return False
        
        if listener.key_mods is not None:
            for kmod in listener.key_mods:
                if kmod == pygame.KMOD_SHIFT and not self.shift_active:
                    return False
                if kmod == pygame.KMOD_LSHIFT and not self.lshift_active:
                    return False
                if kmod == pygame.KMOD_RSHIFT and not self.rshift_active:
                    return False

                if kmod == pygame.KMOD_CTRL and not self.ctrl_active:
                    return False
                if kmod == pygame.KMOD_LCTRL and not self.lctrl_active:
                    return False
                if kmod == pygame.KMOD_RCTRL and not self.rctrl_active:
                    return False

                if kmod == pygame.KMOD_ALT and not self.alt_active:
                    return False
                if kmod == pygame.KMOD_LALT and not self.lalt_active:
                    return False
                if kmod == pygame.KMOD_RALT and not self.ralt_active:
                    return False

        return True
    
    def _buttoncheck(self, listener, event):
        if listener.key is None:
            return True
        if listener.key != event.button:
            return False
        
        if listener.key_mods is not None:
            for kmod in listener.key_mods:
                if kmod == pygame.KMOD_SHIFT and not self.shift_active:
                    return False
                if kmod == pygame.KMOD_LSHIFT and not self.lshift_active:
                    return False
                if kmod == pygame.KMOD_RSHIFT and not self.rshift_active:
                    return False

                if kmod == pygame.KMOD_CTRL and not self.ctrl_active:
                    return False
                if kmod == pygame.KMOD_LCTRL and not self.lctrl_active:
                    return False
                if kmod == pygame.KMOD_RCTRL and not self.rctrl_active:
                    return False

                if kmod == pygame.KMOD_ALT and not self.alt_active:
                    return False
                if kmod == pygame.KMOD_LALT and not self.lalt_active:
                    return False
                if kmod == pygame.KMOD_RALT and not self.ralt_active:
                    return False

        return True

    def addEventListener(self, eventtype, func, once=False, key=None, key_mods:list|None=None, override=False):
        if eventtype not in self.eventListeners:
            raise ValueError("Unknown event type: %s" % eventtype)
        
        if not inspect.iscoroutinefunction(func):
            params = inspect.signature(func).parameters
            def eventListener(e):
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

        if override:
            self._focusEventListeners[eventtype].append(eventListener)
        else:
            self._eventListeners[eventtype].append(eventListener)

        return eventListener.futureWrapper

    def removeEventListener(self, eventListenerFuture: EventListenerFuture):
        len_before = len(self._eventListeners[eventListenerFuture.eventtype]) + len(self._focusEventListeners[eventListenerFuture.eventtype])

        self._eventListeners[eventListenerFuture.eventtype] = [listener for listener in self._eventListeners[eventListenerFuture.eventtype] if id(listener) != eventListenerFuture.id ]
        self._focusEventListeners[eventListenerFuture.eventtype] = [listener for listener in self._focusEventListeners[eventListenerFuture.eventtype] if id(listener) != eventListenerFuture.id ]

        return len_before - len(self._eventListeners[eventListenerFuture.eventtype]) - len(self._focusEventListeners[eventListenerFuture.eventtype])

    def setFocus(self, obj):
        self.focusObj = obj
        self._focus_objid = id(obj)
        self.obj_has_focus = True

    def getFocusObject(self):
        if self.obj_has_focus:
            return self.focusObj
        return None

    def releaseFocus(self, obj):
        if self.obj_has_focus and self._focus_objid == id(obj):
            self.focusObj = None
            self._focus_objid = None
            self.obj_has_focus = False

    @property
    def eventListeners(self):
        return self._eventListeners_cache
    @property
    def focusEventListeners(self):
        return self._focusEventListeners_cache
        
    def __update_event_listeners(self):
        self._eventListeners_cache = deepcopy(self._eventListeners)
        self._focusEventListeners_cache = deepcopy(self._focusEventListeners)

    def queueTask(self, wrapper, args=None):
        self.tasks.put((wrapper, args))

    def queueIntervalEvent(self, func, interval) -> int:
        if isinstance(interval, int):
            interval = datetime.timedelta(seconds=interval)
        e = IntervalEvent(func, interval)
        self._intervalEvents[e.id] = e
        return e.id
        
    def removeIntervalEvent(self, id):
        e = self._intervalEvents.pop(id, None)
        if e is not None:
            return True
        return False



class EventGlobals(object):
    def __init__(self, eventHandler: EventHandler):
        self.eventHandler = eventHandler

    @property
    def mousePos(self):
        return self.eventHandler.mousePosition
    @property
    def tick(self):
        return self.eventHandler._tick

    @property
    def rightShift(self):
        return self.eventHandler.rshift_active
    @property
    def leftShift(self):
        return self.eventHandler.lshift_active
    @property
    def shift(self):
        return self.eventHandler.shift_active

    @property
    def rightCtrl(self):
        return self.eventHandler.rctrl_active
    @property
    def leftCtrl(self):
        return self.eventHandler.lctrl_active
    @property
    def ctrl(self):
        return self.eventHandler.ctrl_active

    @property
    def rightAlt(self):
        return self.eventHandler.ralt_active
    @property
    def leftAlt(self):
        return self.eventHandler.lalt_active
    @property
    def alt(self):
        return self.eventHandler.alt_active
    