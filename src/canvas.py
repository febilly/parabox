import hpprime
from tileset import Tileset

try:
    from typing import Optional, Union
except:
    pass

class Canvas:
    def __init__(self, graphic):
        self.graphic = graphic
        self.width = hpprime.grobw(graphic)
        self.height = hpprime.grobh(graphic)
        pass

    def is_area_visible(self, area: tuple[tuple[int, int], tuple[int, int]]):
        """
        判断此virtual graphic中的area是否与canvas有重叠
        """
        return area[1][0] >= 0 and area[1][1] >= 0 and \
               area[0][0] < self.width and area[0][1] < self.height

    def crop_xy(self, x1, y1, x2, y2):
        """
        将两个坐标对裁剪到canvas的范围扩宽一格内
        """
        x1 = max(x1, -1)
        y1 = max(y1, -1)
        x2 = min(x2, self.width)
        y2 = min(y2, self.height)
        return x1, y1, x2, y2

    def crop_area(self, area: tuple[tuple[int, int], tuple[int, int]]):
        """
        将area裁剪到canvas的范围扩宽一格内
        """
        return self.crop_xy(area[0][0], area[0][1], area[1][0], area[1][1])

    def draw_filled_box_pos(self, x1, y1, x2, y2, color, border_color=None):
        # TODO: adjust the thickness of the border based on the size of the box
        x1, y1, x2, y2 = self.crop_xy(x1, y1, x2, y2)
        if border_color is not None:
            hpprime.fillrect(self.graphic, x1, y1, x2 - x1 + 1, y2 - y1 + 1, border_color, color)
            # hpprime.eval("RECT_P(G{}, {}, {}, {}, {}, {}, {})".format(self.graphic, x1, y1, x2, y2, border_color, color))
        else:
            hpprime.fillrect(self.graphic, x1, y1, x2 - x1 + 1, y2 - y1 + 1, color, color)
            # hpprime.eval("RECT_P(G{}, {}, {}, {}, {}, {})".format(self.graphic, x1, y1, x2, y2, color))

    def draw_filled_box_size(self, x, y, width, height, color, border_color=None):
        self.draw_filled_box_pos(x, y, x + width - 1, y + height - 1, color, border_color)

    def draw_filled_box_area(self, area, color, border_color=None):
        self.draw_filled_box_pos(area[0][0], area[0][1], area[1][0], area[1][1], color, border_color)

    def draw_empty_box_pos(self, x1, y1, x2, y2, color: int):
        # TODO: adjust the thickness of the border based on the size of the box
        x1, y1, x2, y2 = self.crop_xy(x1, y1, x2, y2)
        hpprime.rect(self.graphic, x1, y1, x2 - x1 + 1, y2 - y1 + 1, color)

    def draw_empty_box_size(self, x, y, width, height, color: int):
        self.draw_empty_box_pos(x, y, x + width - 1, y + height - 1, color)

    def draw_empty_box_area(self, area, color: int):
        self.draw_empty_box_pos(area[0][0], area[0][1], area[1][0], area[1][1], color)

    def draw_tile_xy(self, name: str, x, y):
        Tileset().draw_tile_xy(name, self.graphic, x, y)

    def draw_tile_size(self, name: str, x1, y1, width, height):
        Tileset().draw_tile_size(name, self.graphic, x1, y1, width, height)

    def draw_tile_pos(self, name: str, x1, y1, x2, y2):
        Tileset().draw_tile_pos(name, self.graphic, x1, y1, x2, y2)

    def draw_tile_area(self, name: str, area: tuple[tuple[int, int], tuple[int, int]]):
        Tileset().draw_tile_area(name, self.graphic, area)

    def import_graphic(self, source_g: int,
                       source_x=0, source_y=0, source_width=None, source_height=None,
                       target_x=0, target_y=0, target_width=None, target_height=None):
        """
        copy a partial graph "source" into a virtual graph "target"
        """

        source_width = source_width if source_width is not None else hpprime.grobw(source_g)
        source_height = source_height if source_height is not None else hpprime.grobh(source_g)
        target_width = target_width if target_width is not None else source_width
        target_height = target_height if target_height is not None else source_height

        hpprime.strblit2(
            self.graphic, target_x, target_y, target_width, target_height,
            source_g, source_x, source_y, source_width, source_height)


    def copy_to(self, target: Union["Canvas", int],
                source_x=0, source_y=0, source_width=None, source_height=None,
                target_x=0, target_y=0, target_width=None, target_height=None):
        """
        copy a partial virtual graph "source" into another virtual graph "target"
        """

        source_width = source_width if source_width is not None else self.width
        source_height = source_height if source_height is not None else self.height
        target_width = target_width if target_width is not None else source_width
        target_height = target_height if target_height is not None else source_height

        target_g = target if isinstance(target, int) else target.graphic

        hpprime.strblit2(
            target_g, target_x, target_y, target_width, target_height,
            self.graphic, source_x, source_y, source_width, source_height)
