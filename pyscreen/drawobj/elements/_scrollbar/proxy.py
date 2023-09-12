from .base import ScrollProxyBase
from pygame import Surface
from pyscreen.hitbox import Hitbox
from pyscreen.eventHandler import EventHandler
from pyscreen.core.vector import Vector2
import pyscreen.drawobj.draw as draw

SCROLLFLOATER_MINSIZE = 10

class ScrollProxy(ScrollProxyBase):
    def __init__(self, eventHandler: EventHandler, max_width=None, max_height=None, design="Default", background=None, floater_color=(116,116,116), primary_color=(176,176,176), secondary_color=(255,255,255), floater_dragging_color=None):
        super().__init__(eventHandler,max_width,max_height)

        self.design = design if design in ("Default","Modern","Invisible") else "Default"
        self.background = background
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.floater_color = floater_color
        self.floater_dragging_color = floater_dragging_color = floater_color if floater_dragging_color is None else floater_dragging_color


    def render(self, surface: Surface, hitbox_offset: Vector2):
        x, y = surface.get_size()

        show_scroll_bar_x = False
        show_scroll_bar_y = False

        # Determine if scroll bar should be shown
        if self.max_width is not None and x > self.max_width:
            show_scroll_bar_x = True
            self.scroll_maxoffset.x = x - self.max_width
        else:
            self.scroll_maxoffset.x = 0

        if self.max_height is not None and y > self.max_height:
            show_scroll_bar_y = True
            self.scroll_maxoffset.y = y - self.max_height
        else:
            self.scroll_maxoffset.y = 0

        # Calculate required space for Surface
        req_x = (x + 10) if self.design in ("Default") and show_scroll_bar_x else x
        req_y = (y + 10) if self.design in ("Default") and show_scroll_bar_y else y
        
        surf_width = req_x
        if self.max_width is not None:
            surf_width = min( req_x , self.max_width)

        surf_height = req_y
        if self.max_height is not None:
            surf_height = min( req_y , self.max_height)

        # Create Surface
        proxy_surface = Surface((surf_width, surf_height))
        self._set_hitbox(proxy_surface, hitbox_offset)
        if self.background is not None:
            proxy_surface.fill(self.background)
        
        # Calculate available space
        avail_x = surf_width - 10 if self.design in ("Default") and show_scroll_bar_x else surf_width
        avail_y = surf_height - 10 if self.design in ("Default") and show_scroll_bar_y else surf_height

        # Blit Surfaces
        scl_x, scl_y = (-self.scroll_offset).asInts()
        surface.scroll(scl_x, scl_y)
        proxy_surface.blit(surface, (0,0))

        # Draw Scrollbar
        if self.design == "Default":
            self._draw_default(proxy_surface, show_scroll_bar_x, show_scroll_bar_y)
        elif self.design == "Modern":
            raise NotImplementedError
            self._draw_modern(proxy_surface, show_scroll_bar_x, show_scroll_bar_y)

        return proxy_surface
        

    def _draw_default(self, surface: Surface, show_scroll_bar_x: bool, show_scroll_bar_y: bool):
        surf_x, surf_y = surface.get_size()

        scroll_x_width = surf_x
        scroll_y_height = surf_y

        if show_scroll_bar_x and show_scroll_bar_y:
            scroll_x_width = surf_x - 10
            scroll_y_height = surf_y - 10

        # Vertical Scrollbar Background
        if show_scroll_bar_y and self.scroll_maxoffset.y != 0:
            p1 = (surf_x - 10, 0)
            p2 = (surf_x, surf_y)

            #bg
            draw.rectangle(surface, self.secondary_color, p1, p2)

            p1 = (surf_x - 10, 0)
            p2 = (surf_x - 10, surf_y)

            #side
            draw.line(surface, self.secondary_color, p1, p2, 1)

            floater_size_y = max(SCROLLFLOATER_MINSIZE, (scroll_y_height - self.scroll_maxoffset.y) )
            floater_area_y = scroll_y_height - floater_size_y

            floater_position_y = int(floater_area_y * (self.scroll_offset.y / self.scroll_maxoffset.y))
        
            p1 = (surf_x-9, floater_position_y)
            p2 = (surf_x, floater_position_y+floater_size_y)
            draw.rectangle(surface,self.floater_color,p1,p2)

        # Horizontal Scrollbar Background
        if show_scroll_bar_x and self.scroll_maxoffset.x != 0:
            p1 = (0, surf_y - 10)
            p2 = (surf_x, surf_y)

            #bg
            draw.rectangle(surface, self.secondary_color, p1, p2)

            p1 = (0, surf_y - 10)
            p2 = (surf_x, surf_y - 10)

            #side
            draw.line(surface, self.secondary_color, p1, p2, 1)

            floater_size_x = max(SCROLLFLOATER_MINSIZE, (scroll_x_width - self.scroll_maxoffset.x) )
            floater_area_x = scroll_x_width - floater_size_x

            floater_position_x = int(floater_area_x * (self.scroll_offset.x / self.scroll_maxoffset.x))

            p1 = (floater_position_x, surf_y-9)
            p1 = (floater_position_x+floater_size_x, surf_y)
            draw.rectangle(surface,self.floater_color,p1,p2)