from pygame import SRCALPHA, Surface, Rect

from pyscreen.core.vector import Vector2, IntVector2
from pyscreen.drawobj.util.background import BackgroundImage

from .base import Element

# sizeProvider: provider for width and height
# margin: provider for margin in pixels (positive int) or percentage (float between 0 and 1)
# padding: provider for padding in pixels (positive int) or percentage (float between 0 and 1)

BOX_MIN_WIDTH = 10
BOX_MIN_HEIGHT = 10

class Box(Element):
    """ Like a HTML Div """

    def __init__(self, objects: list|None = None, location: Vector2|tuple = (0,0), margin: Vector2|tuple = (0,0,0,0), padding: tuple = (0,0,0,0), gap: int = 1,
        alignment: str = "stretch", background: None|tuple|BackgroundImage = None, height: int|None = None, width: int|None = None
    ):
        Element.__init__(self, width=width, height=height, padding=padding, margin=margin)

        self._scoll_height = 0
        self._visible = True

        alignment = alignment.lower()
        if alignment not in ('left', 'right', 'center', 'stretch'):
            raise ValueError("invalid alignment: '%s'" % alignment)
        self._alignment = alignment
        self._background = background
        self._gap = gap
        self.location = Vector2(location)
        self.absolute_offset = Vector2(location)
        self.margin_selfcontrol = True

        self._objects: list = list(objects) if objects is not None else []
        self._obj_sizes: dict[int,tuple[int,int]] = {}
        self._obj_surf_pos: dict[int,tuple[int,int]] = {}
        self._surface = None

    def destruct(self):
        self.clear()
        self._surface = None

    def clear(self):
        for obj in self._objects:
            obj.destruct()
        self._objects = []

    def contains(self, objects: list):
        self._objects: list[Element] = objects

    def append(self, *obj: Element):
        for o in obj:
            self.objects.append(o)

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self, value):
        self._objects = value
        self._changed = True

    @property
    def width(self):
        if not self._visible:
            return 0
        if self._width is not None:
            return self._width
        return self._calc_innerwidth() + self.padding.left + self.padding.right

    @width.setter
    def width(self, value):
        if value is None:
            self._width = None
            return
        if value < 0:
            raise ValueError("height cannot be negative")
        self._width = value
        self._changed = True

    @property
    def innerwidth(self):
        if not self._visible:
            return 0
        if self._width is not None:
            return max(self._width - self.padding.left - self.padding.right, 0)
        return self._calc_innerwidth()
    
    def _calc_innerwidth(self):
        iw = 0
        for obj in self._objects:
            if not obj.visible:
                continue
            iw = max(iw, obj.width + obj.margin.left + obj.margin.right)
        return iw

    @property
    def height(self):
        if not self._visible:
            return 0
        if self._height is not None:
            return self._height
        return self._calc_innerheight() + self.padding.top + self.padding.bottom

    @height.setter
    def height(self, value):
        if value is None:
            self._height = None
            return
        if value < 0:
            raise ValueError("height cannot be negative")
        self._changed = True
        self._height = value

    @property
    def innerheight(self):
        if not self._visible:
            return 0
        if self._height is not None:
            return max(self._height - self.padding.top - self.padding.bottom, 0)
        return self._calc_innerheight()

    def _calc_innerheight(self):
        h = 0
        first = True
        margin_bottom = 0
        for obj in self._objects:
            if not obj.visible:
                continue
            if first:
                first = False
            else:
                h += self._gap
            h += max(margin_bottom, obj.margin.top)
            h += obj.height
            margin_bottom = obj.margin.bottom
        return h + margin_bottom

    @property
    def hasFocusObject(self):
        for obj in self._objects:
            if getattr(obj, "hitbox", None) is not None and obj.hitbox.hasFocus:
                return True
            elif getattr(obj, "hasFocusObject", None) is not None and obj.hasFocusObject:
                return True
        return False

    @property
    def position(self):
        """ Returns the position of the box relative to its parent (includes margin)"""
        x = self.location[0] + self.margin.left
        y = self.location[1] + self.margin.top
        return IntVector2(x,y)

    @property
    def changed(self):
        if self._surface is None or self._changed:
            return True
        if self._last_height != self.height or self._last_width != self.width:
            return True
        if len(self._objects) != len(self._obj_sizes):
            return True
        return self._changed or any([o.changed for o in self._objects])

    def _needs_rebuild(self):
        if self._surface is None or self._changed:
            return True
        if self._last_height != self.height or self._last_width != self.width:
            return True
        if len(self._objects) != len(self._obj_sizes):
            return True
        return any([ self._obj_sizes[i] != (o.width, o.height) for i, o in enumerate(self._objects)])

    def render(self, surface: Surface|None = None):
        if self.changed:
            if self._needs_rebuild():
                self._build()
            else:
                self._update()

            self._last_height = self.height
            self._last_width = self.width
            self._changed = False

        if surface is not None:
            surface.blit(self._surface, tuple(self.position))
        
        self._changed = False
        return self._surface

    def _update(self):
        for i, obj in enumerate(self._objects):
            if obj.changed:
                size = (obj.width, obj.height)
                location = self._obj_surf_pos[i]
                rect = Rect(location, size)

                if self._background is not None:
                    self._surface.fill(self._background, rect)
                else:
                    self._surface.fill((0,0,0,0), rect)
                s = obj.render()
                self._surface.blit(s, rect)

    def _build(self):
        h = self.padding.top
        r_h = h - self._scoll_height

        class SubSurface:
            def __init__(self, obj: Element, surface: Surface):
                self.obj: Element = obj
                self.surface: Surface = surface


        sub_surfaces: dict[int, SubSurface] = {}
        flex_objs: dict[int, Box] = {}

        iw = 0

        for i, obj in enumerate(self._objects):
            if not obj.visible:
                continue
            if isinstance(obj, Box):
                if obj.settedHeight is None:
                    flex_objs[i] = obj
                    continue

            with obj.resetAfter():
                # change width if needed
                if self._alignment == "stretch":
                    obj.width = self.innerwidth
                elif self._alignment == "center":
                    if obj.width > self.innerwidth:
                        obj.width = self.innerwidth

                # render object
                surf = obj.render()
                iw = max(iw, obj.width)

            sub_surfaces[i] = SubSurface(obj, surf)

            h += obj.height + self._gap

        self._surface = Surface((self.width, self.height), SRCALPHA, 32)

        if self._background is not None:
            loc = (0,0)
            size = (self.width, self.height)
            rect = Rect(loc, size)
            if isinstance(self._background, BackgroundImage):
                self._surface.blit(self._background.render_scaled(size), rect)
            else:
                self._surface.fill(self._background, rect)

        available_height = self.innerheight - h + self._gap
        if len(flex_objs) > 0:
            available_height_per_obj = round(available_height // len(flex_objs))

            for i, flex_obj in flex_objs.items():
                flex_obj.height = max(available_height_per_obj - self._gap, BOX_MIN_HEIGHT)
                flex_obj.width = self.innerwidth
                surf = flex_obj.render()
                sub_surfaces[i] = SubSurface(flex_obj, surf)

                h += flex_obj.height + self._gap


        local_margin_bottom = 0
        for i in sorted(sub_surfaces):
            sub_surface = sub_surfaces[i]

            surf = sub_surface.surface
            sObj = sub_surface.obj

            if surf is None:
                continue

            xLoc = 0
            if self._alignment == "center":
                if sObj.width < self.innerwidth:
                    xLoc = round(self.innerwidth / 2 - sObj.width / 2)
            elif self._alignment == "right":
                xLoc = self.innerwidth - sObj.width

            xLoc += self.padding.left
            xLoc += sObj.margin.left

            y_margin_offset = max(local_margin_bottom, sObj.margin.top)

            yLoc = r_h
            yLoc += y_margin_offset

            local_margin_bottom = sObj.margin.bottom
                

            s_height = surf.get_height()
            relLocation = (xLoc, yLoc)
            absLocation = (self.absolute_offset + relLocation)
            if self.margin_selfcontrol:
                absLocation += (self.margin.left, self.margin.top)
            
            self._objects[i].setOffset(absLocation)
            self._surface.blit(surf, relLocation)

            r_h += s_height + self._gap + y_margin_offset
                
    def setOffset(self, offset: Vector2):
        self.absolute_offset: Vector2 = offset
        self.margin_selfcontrol = False

    def printHitbox(self, surface: Surface):
        for obj in self._objects:
            if hasattr(obj, "printHitbox"):
                obj.printHitbox(surface)



class HorizontalBox(Box):
    def __init__(self, objects: list|None = None, location: Vector2|tuple = (0,0), margin: Vector2|tuple = (0,0,0,0), padding: tuple = (0,0,0,0), gap: int = 1,
        alignment: str = "stretch", background: None|tuple|BackgroundImage = None, height: int|None = None, width: int|None = None
    ):
        super().__init__(objects, location, margin, padding, gap, "stretch", background, height, width)
        if alignment not in ('top', 'bottom', 'center', 'stretch'):
            raise ValueError("invalid alignment: '%s'" % alignment)
        self._alignment = alignment

    def _calc_innerheight(self):
        ih = 0
        for obj in self._objects:
            if not obj.visible:
                continue
            ih = max(ih, obj.height + obj.margin.top + obj.margin.bottom)
        return ih

    def _calc_innerwidth(self):
        w = 0
        first = True
        margin_right = 0
        for obj in self._objects:
            if not obj.visible:
                continue
            if first:
                first = False
            else:
                w += self._gap
            w += max(margin_right, obj.margin.left)
            w += obj.width
            margin_right = obj.margin.right
        return w + margin_right

    def _build(self):
        w = self.padding.left
        r_w = w

        class SubSurface:
            def __init__(self, obj: Element, surface: Surface):
                self.obj: Element = obj
                self.surface: Surface = surface


        sub_surfaces: dict[int, SubSurface] = {}
        flex_objs: dict[int, Box] = {}

        ih = 0

        for i, obj in enumerate(self._objects):
            if not obj.visible:
                continue
            if isinstance(obj, Box):
                if obj.settedWidth is None:
                    flex_objs[i] = obj
                    continue

            with obj.resetAfter():
                if self._alignment == "stretch":
                    obj.height = self.innerwidth
                elif self._alignment == "center":
                    if obj.height > self.innerheight:
                        obj.height = self.innerheight

                # render object
                surf = obj.render()
                ih = max(ih, obj.height)

            sub_surfaces[i] = SubSurface(obj, surf)

            w += obj.width + self._gap

        self._surface = Surface((self.width, self.height), SRCALPHA, 32)

        if self._background is not None:
            loc = (0,0)
            size = (self.width, self.height)
            rect = Rect(loc, size)
            if isinstance(self._background, BackgroundImage):
                self._surface.blit(self._background.render_scaled(size), rect)
            else:
                self._surface.fill(self._background, rect)

        available_width = self.innerwidth - w + self._gap
        if len(flex_objs) > 0:
            available_width_per_obj = round(available_width // len(flex_objs))

            for i, flex_obj in flex_objs.items():
                flex_obj.width = max(available_width_per_obj - self._gap, BOX_MIN_HEIGHT)
                flex_obj.height = self.innerheight
                surf = flex_obj.render()
                sub_surfaces[i] = SubSurface(flex_obj, surf)

                w += flex_obj.width + self._gap


        local_margin_right = 0
        for i in sorted(sub_surfaces):
            sub_surface = sub_surfaces[i]

            surf = sub_surface.surface
            sObj = sub_surface.obj

            if surf is None:
                continue

            yLoc = 0
            if self._alignment == "center":
                if sObj.height < self.innerheight:
                    yLoc = round(self.innerheight / 2 - sObj.height / 2)
            elif self._alignment == "bottom":
                yLoc = self.innerheight - sObj.height

            yLoc += self.padding.top
            yLoc += sObj.margin.top

            x_margin_offset = max(local_margin_right, sObj.margin.left)

            xLoc = r_w
            xLoc += x_margin_offset

            local_margin_right = sObj.margin.right
                

            s_width = surf.get_width()
            relLocation = (xLoc, yLoc)
            absLocation = (self.absolute_offset + relLocation)
            if self.margin_selfcontrol:
                absLocation += (self.margin.left, self.margin.top)
            
            self._objects[i].setOffset(absLocation)
            self._surface.blit(surf, relLocation)

            r_w += s_width + self._gap + x_margin_offset
