from functools import lru_cache
from typing import Generator, Iterable, overload

from pygame import Surface
import pygame
from pyscreen.core.vector import Vector2
from pyscreen.drawobj.elements.base import Element
from pyscreen.drawobj.elements.flexbox import Flexbox
from pyscreen.drawobj.elements.box import Box


class GridCell(Box):
    def __init__(self, objects: list|None = None, colSize: int = 1, rowSize: int = 1, **kwargs):
        super().__init__(objects, **kwargs)

        assert colSize > 0 and rowSize > 0, "colSize and rowSize must be greater than 0"

        self.colSize = colSize
        self.rowSize = rowSize


class Grid(Element):
    def __init__(self, position = None, padding = (0,0,0,0), margin = (0,0,0,0), width: int = None, height: int = None, *,columns = 1, rows = 1, rowTemplate = None, colTemplate = None):
        super().__init__(padding=padding, margin=margin, width=width, height=height)
        
        self._columns = columns
        self._rows = rows

        self._cellSets: dict[tuple[int,int],set[GridCell]] = {}

        self._changed = True
        self.position: Vector2 = Vector2(position) if position is not None else Vector2(0,0)

        self._rowTemplate: str = rowTemplate
        self._colTemplate: str = colTemplate

        self._rowHeights = [None] * rows
        self._colWidths = [None] * columns

        self._flexCols = []
        self._flexRows = []

        self._surface: Surface | None = None

        self.absolute_offset: Vector2 = Vector2(0,0)

        self._calculateSizes()

    def destruct(self):
        self.clear()
        self._surface = None

    def clear(self):
        for cellSet in self._cellSets.values():
            for cell in cellSet:
                cell.destruct()
        self._cellSets.clear()

    def printHitbox(self, surface: Surface):
        for cellSet in self._cellSets.values():
            for cell in cellSet:
                cell.printHitbox(surface)

    def addCell(self, cell: GridCell, col: int, row: int):
        if col < 0 or col >= self._columns:
            raise KeyError("col must be in range [0, columns)")
        if row < 0 or row >= self._rows:
            raise KeyError("row must be in range [0, rows)")

        if (col, row) in self._cellSets:
           self._cellSets[(col, row)].add(cell) 
        else:
            self._cellSets[(col, row)] = {cell}

    def removeCell(self, cell: GridCell, col: int, row: int):
        if col < 0 or col >= self._columns:
            raise KeyError("col must be in range [0, columns)")
        if row < 0 or row >= self._rows:
            raise KeyError("row must be in range [0, rows)")

        if (col, row) in self._cellSets:
            self._cellSets[(col, row)].remove(cell)

    def getCell(self, col: int, row: int) -> list[GridCell]|None:
        if col < 0 or col >= self._columns:
            raise KeyError("col must be in range [0, columns)")
        if row < 0 or row >= self._rows:
            raise KeyError("row must be in range [0, rows)")

        return self._cellSets.get((col, row), None)
    
    def columnItems(self, col: int, skipEmpty=True) -> Iterable[list[GridCell]|None]:
        if col < 0 or col >= self._columns:
            raise KeyError("col must be in range [0, columns)")

        for row in range(self._rows):
            item = self._cellSets.get((col, row), None)
            if item is not None or not skipEmpty:
                yield item
    
    def rowItems(self, row: int, skipEmpty=True) -> Iterable[list[GridCell]|None]:
        if row < 0 or row >= self._rows:
            raise KeyError("row must be in range [0, rows)")
        
        for col in range(self._columns):
            item = self._cellSets.get((col, row), None)
            if item is not None or not skipEmpty:
                yield item


    @property
    def columns(self) -> int:
        return self._columns
    
    @overload
    def setColumns(self, value: int):...
    @overload
    def setColumns(self, value: int, suppressWarning: bool = False):
        if self._colTemplate is not None and not suppressWarning:
            raise Warning("Setting columns will override column template")
        
        self._columns = value
        self._colTemplate = None
        self._calculateSizes()

    @property
    def rows(self) -> int:
        return self._rows
    
    @overload
    def setRows(self, value: int):...
    @overload
    def setRows(self, value: int, suppressWarning: bool = False):
        if self._rowTemplate is not None and not suppressWarning:
            raise Warning("Setting rows will override row template")
        
        self._rows = value
        self._rowTemplate = None
        self._calculateSizes()

    @property
    def rowTemplate(self) -> str:
        return self._rowTemplate
    
    @rowTemplate.setter
    def rowTemplate(self, value: str):
        self._rowTemplate = value
        self._calculateSizes()

    @property
    def colTemplate(self) -> str:
        return self._colTemplate
    
    @colTemplate.setter
    def colTemplate(self, value: str):
        self._colTemplate = value
        self._calculateSizes()


    def _calculateSizes(self):
        if self._colTemplate is None:
            self._colWidths = [None] * self._columns
        else:
            properties: list[str] = self._colTemplate.split()

            self._colWidths = [None] * len(properties)
            self._columns = len(properties)

            self._flexCols = []

            for i, prop in enumerate(properties):
                if prop.endswith("px"):
                    v = int(prop[:-2])
                    assert v >= 0, "Invalid column template"
                    self._colWidths[i] = v

                elif prop.endswith("%"):
                    v = float(prop[:-1])
                    assert v >= 0, "Invalid column template"
                    assert v < 100, "Invalid column template"
                    self._colWidths[i] = v / 100

                elif prop == "auto":
                    self._flexCols.append(i)

                else:
                    raise ValueError("Invalid column template")
        
        if self._rowTemplate is None:
            self._rowHeights = [None] * self._rows
        else:
            properties: list[str] = self._rowTemplate.split()

            self._rowHeights = [None] * len(properties)
            self._rows = len(properties)

            self._flexRows = []

            for i, prop in enumerate(properties):
                if prop.endswith("px"):
                    v = int(prop[:-2])
                    assert v >= 0, "Invalid row template"
                    self._rowHeights[i] = v

                elif prop.endswith("%"):
                    v = float(prop[:-1])
                    assert v >= 0, "Invalid row template"
                    assert v < 100, "Invalid row template"
                    self._rowHeights[i] = v / 100

                elif prop == "auto":
                    self._flexRows.append(i)

                else:
                    raise ValueError("Invalid row template")
                
    
    def _calculateColFlexSpace(self) -> int:

        flexSpaceCols = self.innerwidth
        for cw in self._colWidths:
            if cw is None:
                continue
            if isinstance(cw, int):
                flexSpaceCols -= cw
            else:
                flexSpaceCols -= int(cw * self.innerwidth)

        if flexSpaceCols < 0:
            flexSpaceCols = 0

        return int(flexSpaceCols)


    def _calculateRowFlexSpace(self) -> int:
        
        flexSpaceRows = self.innerheight
        for rh in self._rowHeights:
            if rh is None:
                continue
            if isinstance(rh, int):
                flexSpaceRows -= rh
            else:
                flexSpaceRows -= int(rh * self.innerheight)
        
        return int(flexSpaceRows)

    def _calculateColWidth(self) -> list[int]:
        flexCount = self._colWidths.count(None)
        if flexCount != 0:
            flexSpace = self._calculateColFlexSpace() // flexCount

        widths = [0] * len(self._colWidths)

        for i, cw in enumerate(self._colWidths):
            if cw is None:
                widths[i] = flexSpace
            elif isinstance(cw, int):
                widths[i] = cw
            else:
                widths[i] = int(cw * self.innerwidth)

        return widths

    def _calculateRowHeight(self) -> list[int]:
        flexCount = self._rowHeights.count(None)
        if flexCount != 0:
            flexSpace = self._calculateRowFlexSpace() // flexCount

        heights = [0] * len(self._rowHeights)

        for i, rh in enumerate(self._rowHeights):
            if rh is None:
                heights[i] = flexSpace
            elif isinstance(rh, int):
                heights[i] = rh
            else:
                heights[i] = int(rh * self.innerheight)

        return heights
    

    def render(self, surface: Surface | None = None):
        self._surface = Surface((self.width, self.height), pygame.SRCALPHA, 32)

        colWidths = self._calculateColWidth()
        rowHeights = self._calculateRowHeight()

        for (xPos, yPos), cellSet in self._cellSets.items():
            for cell in cellSet:
                self.renderCell(cell, xPos, yPos, colWidths, rowHeights)
        
        if surface is not None:
            surface.blit(self._surface, (self.position.x, self.position.y))
        return self._surface

    def renderCell(self, cell: GridCell, xPos: int, yPos: int, colWidths: list[int], rowHeights: list[int]):
        cellWidth = sum(colWidths[xPos:xPos + cell.colSize]) - cell.margin.width
        cellHeight = sum(rowHeights[yPos:yPos + cell.rowSize]) - cell.margin.height

        x = sum(colWidths[:xPos]) + self.padding.left + cell.margin.left
        y = sum(rowHeights[:yPos]) + self.padding.top + cell.margin.top

        cell.setOffset(self.absolute_offset + (x, y))

        with cell.resetAfter():
            cell.width = cellWidth
            cell.height = cellHeight
            self._surface.blit(cell.render(), (x, y))


    def setOffset(self, offset: Vector2):
        self.absolute_offset: Vector2 = offset


    def _calc_innerheight(self):
        min_height = 0
        row_min_heights = [0] * self._rows
        multirow_cells: list[tuple[int,GridCell]] = []
        for (row,col), cellSet in self._cellSets.items():
            for cell in cellSet:
                if cell.rowSize > 1:
                    multirow_cells.append((row, cell))
                else:
                    row_min_heights[row] = max(row_min_heights[row], cell.height + cell.margin.height)

        if multirow_cells:
            for row, multirow_cell in multirow_cells.sort(key=lambda x: x[0]):
                row_height = sum(row_min_heights[row:row + multirow_cell.rowSize])
                req_height = multirow_cell.height + multirow_cell.margin.height
                if req_height > row_height:
                    diff = req_height - row_height
                    row_min_heights[row + multirow_cell.rowSize - 1] += diff

        if self._rowTemplate is not None:
            for i, r in enumerate(self._rowHeights):
                if isinstance(r, int):
                    row_min_heights[i] = r
                elif isinstance(r, float):
                    min_height = max(min_height, int(row_min_heights[i] / r))
        else:
            return max(row_min_heights) * self._rows

        return max(min_height,sum(row_min_heights))
    
    def _calc_innerwidth(self):
        min_width = 0
        col_min_widths = [0] * self._columns
        multicolumn_cells: list[tuple[int,GridCell]] = []
        for (row,col), cellSet in self._cellSets.items():
            for cell in cellSet:
                if cell.colSize > 1:
                    multicolumn_cells.append((col, cell))
                else:
                    col_min_widths[col] = max(col_min_widths[col], cell.width + cell.margin.width)

        if multicolumn_cells:
            for col, multicolumn_cell in multicolumn_cells.sort(key=lambda x: x[0]):
                col_width = sum(col_min_widths[col:col + multicolumn_cell.colSize])
                req_width = multicolumn_cell.width + multicolumn_cell.margin.width
                if req_width > col_width:
                    diff = req_width - col_width
                    col_min_widths[col + multicolumn_cell.colSize - 1] += diff

        if self._colTemplate is not None:
            for i, c in enumerate(self._colWidths):
                if isinstance(c, int):
                    col_min_widths[i] = c
                elif isinstance(c, float):
                    min_width = max(min_width, int(col_min_widths[i] / c))
        else:
            return max(col_min_widths) * self._columns

        return max(min_width,sum(col_min_widths))