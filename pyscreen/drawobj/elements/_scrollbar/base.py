from pyscreen.drawobj.elements.base import Element
from pygame import Surface
from pyscreen.hitbox import Hitbox
from pyscreen.eventHandler import EventHandler
from pyscreen.core.vector import Vector2

SCROLL_STEPS = 30

class ScrollProxyBase(Element):
    # Uses custom hitbox logic => no ElementWithHitbox
    def __init__(self, eventHandler: EventHandler, max_width=None, max_height=None):
        self.eventHandler: EventHandler = eventHandler
        self.max_width = max_width
        self.max_height = max_height
        self.hitbox: Hitbox = None
        self.scroll_offset = Vector2(0,0)
        self.scroll_maxoffset = Vector2(0,0)


    def __del__(self):
        self.hitbox.destruct()
        

    def destruct(self):
        self.hitbox.destruct()
        self.hitbox = None

    def _set_hitbox(self, surface: Surface, hitbox_offset: Vector2):
        s = surface.get_size()

        if self.hitbox is None:
            self.hitbox = Hitbox(self.eventHandler, hitbox_offset, s, target=self)
            self.hitbox.addEventListener("scrollUp",self.scroll_up)
            self.hitbox.addEventListener("scrollDown",self.scroll_down)
        else:
            self.hitbox.hitbox_location = hitbox_offset
            self.hitbox.hitbox_size = s


    def scroll_up(self, e):
        if self.eventHandler.shift_active:
            self.scroll_offset.x = self.scroll_offset.x - SCROLL_STEPS
            if self.scroll_offset.x < 0:
                self.scroll_offset.x = 0
        else:
            self.scroll_offset.y = self.scroll_offset.y - SCROLL_STEPS
            if self.scroll_offset.y < 0:
                self.scroll_offset.y = 0

    def scroll_down(self, e):
        if self.eventHandler.shift_active:
            self.scroll_offset.x = self.scroll_offset.x + SCROLL_STEPS
            if self.scroll_offset.x > self.scroll_maxoffset.x:
                self.scroll_offset.x = self.scroll_maxoffset.x
        else:
            self.scroll_offset.y = self.scroll_offset.y + SCROLL_STEPS
            if self.scroll_offset.y > self.scroll_maxoffset.y:
                self.scroll_offset.y = self.scroll_maxoffset.y

    def render(self, surface: Surface):
        raise NotImplementedError

