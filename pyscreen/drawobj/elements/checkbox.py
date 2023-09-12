from pygame import K_BACKSPACE, K_RETURN, SRCALPHA, Surface
from pygame.font import Font

import pyscreen.drawobj.draw as draw
from pyscreen.core.vector import Vector2
from pyscreen.eventHandler import EventHandler
from pyscreen.hitbox import Hitbox

from .base import ElementWithHitbox


class Checkbox(ElementWithHitbox):
    def __init__(self, eventHandler: EventHandler, font: Font, location: tuple|Vector2 = (0,0),
                 width:int|None=None, height:int|None=None, background=None, color=(255,255,255), 
                 border_color=None, checked=False, value="", max_length=None, padding=(2,8,2,8), margin=(2,8,2,8),
                 cb_border=(0,0,0),cb_background=(255,255,255),cb_color=(0,0,0),cb_color_inactive=None,symbol="checkmark"):
        super().__init__(eventHandler, padding, margin, width, height)
        self._cb_border = cb_border
        self._cb_background = cb_background
        self._cb_color = cb_color
        self._cb_color_inactive = cb_color_inactive
        self._symbol = symbol if symbol in ("checkmark","cross","circle","filled","circle_filled") else "checkmark"
        self._font = font
        self.location = Vector2(location)
        self._background = background
        self._color = color
        self._border = border_color
        self._checked = checked
        self._value = value
        self.max_length = max_length

        self.hitbox.addEventListener("mouseClick", self._change_checked)

        self.__override_event = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._changed = True

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        self._changed = True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._changed = True

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, value):
        self._border = value
        self._changed = True

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value
        self._changed = True

    @property
    def cb_background(self):
        return self._cb_background

    @cb_background.setter
    def cb_background(self, value):
        self._cb_background = value
        self._changed = True

    @property
    def cb_color(self):
        return self._cb_color

    @cb_color.setter
    def cb_color(self, value):
        self._cb_color = value
        self._changed = True

    @property
    def cb_color_inactive(self):
        return self._cb_color_inactive

    @cb_color_inactive.setter
    def cb_color_inactive(self, value):
        self._cb_color_inactive = value
        self._changed = True

    @property
    def cb_border(self):
        return self._cb_border

    @cb_border.setter
    def cb_border(self, value):
        self._cb_border = value
        self._changed = True

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value
        self._changed = True

    def _change_checked(self,e=None):
        self._changed = True
        self._checked = not self._checked

    def render(self, surface: Surface|None = None):
        if not self.visible:
            return

        # Show text
        show_value = self._value

        text_surface = self._font.render(show_value, True, self._color, self._background)
        frame_surface = Surface(
            (self.width, self.height), SRCALPHA, 32
        )

        if self._background is not None:
            frame_surface.fill(self._background)

        if self._border is not None:
            sx, sy = frame_surface.get_size()
            draw.rectangle(frame_surface,self._border,(0,0),(sx,sy),1)

        dx,dy = (self.padding.left+self.innerheight+2,self.padding.top)

        frame_surface.blit(text_surface, (dx,dy))

        # Show checkbox
        symbol_color = self._cb_color if self._checked else self._cb_color_inactive

        checkbox_surface = Surface(
            (self.innerheight, self.innerheight), SRCALPHA, 32
        )
        box_frame_size = Vector2(self.innerheight, self.innerheight)
        box_margin = self.innerheight // 20
        box_top_left = Vector2(box_margin,box_margin)
        box_bottom_right = box_frame_size - box_top_left
        box_size = box_bottom_right - box_top_left
        cb_border = self._cb_border
        cb_bg = self._cb_background
        #background
        if self._symbol == "filled":
            if symbol_color is not None:
                cb_bg = symbol_color
            draw.rectangle(checkbox_surface,cb_bg,box_top_left,box_bottom_right,0)
        else:
            draw.rectangle(checkbox_surface,cb_bg,box_top_left,box_bottom_right,0)
            #symbol
            if symbol_color is not None:
                if self._symbol == "checkmark":
                    p1 = (box_size * (0.1,0.7) + box_top_left).asInts()
                    p2 = (box_size * (0.4,0.9) + box_top_left).asInts()
                    p3 = (box_size * (0.9,0.1) + box_top_left).asInts()
                    draw.aaline(checkbox_surface,symbol_color,p1,p2,2)
                    draw.aaline(checkbox_surface,symbol_color,p2,p3,2)
                elif self._symbol == "cross":
                    p1 = box_top_left + (1,1)
                    p2 = box_bottom_right - (1,1)
                    p3 = (box_size * (1,0) + box_top_left).asInts() + (-1,1)
                    p4 = (box_size * (0,1) + box_top_left).asInts() + (1,-1)
                    draw.aaline(checkbox_surface,symbol_color,p1,p2,2)
                    draw.aaline(checkbox_surface,symbol_color,p3,p4,2)
                elif self._symbol == "circle":
                    p1 = box_top_left + (1,1)
                    p2 = box_bottom_right - (1,1)
                    draw.circle(checkbox_surface,symbol_color,p1,p2,2)
                elif self._symbol == "circle_filled":
                    p1 = box_top_left + (1,1)
                    p2 = box_bottom_right - (1,1)
                    draw.aacircle(checkbox_surface,symbol_color,p1,p2,True)
        #border
        draw.rectangle(checkbox_surface,cb_border,box_top_left,box_bottom_right,1)

        frame_surface.blit(checkbox_surface, (self.padding.left,self.padding.top))

        # final blit
        if surface is not None:
            self.hitbox.hitbox_location: Vector2 = self.location
            surface.blit(frame_surface, tuple(self.location))

        self.hitbox.hitbox_size = Vector2(frame_surface.get_size())
        self._changed = False
        return frame_surface

    def _calc_innerheight(self):
        return self._font.get_height()

    def _calc_innerwidth(self):
        show_value = self._value
        if self.hitbox is None or self.hitbox.hasFocus:
            show_value += " "

        text_surface = self._font.render(show_value, False, (0,0,0))
        x,y = text_surface.get_size()
        return x