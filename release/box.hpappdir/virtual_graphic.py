import hpprime
from tileset import Tileset

class VirtualGraphic:
    def __init__(self, canvas, start_x, start_y, width, height):
        self.canvas = canvas
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        pass

    def draw_filled_box_pos(self, x1, y1, x2, y2, color, border_color=None):
        # TODO: adjust the thickness of the border based on the size of the box
        if border_color is not None:
            # fuck you hp
            # hpprime.fillrect(self.canvas, self.start_x + x, self.start_y + y, width, height, border_color, color)
            hpprime.eval("RECT_P(G{}, {}, {}, {}, {}, {}, {})".format(self.canvas, self.start_x + x1, self.start_y + y1, self.start_x + x2, self.start_y + y2, border_color, color))
        else:
            # hpprime.fillrect(self.canvas, self.start_x + x, self.start_y + y, width, height, color, color)
            hpprime.eval("RECT_P(G{}, {}, {}, {}, {}, {})".format(self.canvas, self.start_x + x1, self.start_y + y1, self.start_x + x2, self.start_y + y2, color))

    def draw_filled_box_size(self, x, y, width, height, color, border_color=None):
        self.draw_filled_box_pos(x, y, x + width - 1, y + height - 1, color, border_color)

    def draw_filled_box_area(self, area, color, border_color=None):
        self.draw_filled_box_pos(area[0][0], area[0][1], area[1][0], area[1][1], color, border_color)

    def draw_empty_box_size(self, x, y, width, height, color     ):
        # TODO: adjust the thickness of the border based on the size of the box
        hpprime.rect(self.canvas, self.start_x + x, self.start_y + y, width, height, color)

    def draw_empty_box_pos(self, x1, y1, x2, y2, color     ):
        self.draw_empty_box_size(x1, y1, x2 - x1 + 1, y2 - y1 + 1, color)

    def draw_empty_box_area(self, area, color     ):
        self.draw_empty_box_size(area[0][0], area[0][1], area[1][0] - area[0][0] + 1, area[1][1] - area[0][1] + 1, color)

    def draw_tile_size(self, name     , x, y):
        Tileset().draw_tile_xy(name, self.canvas, self.start_x + x, self.start_y + y)

    def draw_tile_pos(self, name     , x1, y1, x2, y2):
        Tileset().draw_tile_size(name, self.canvas, self.start_x + x1, self.start_y + y1, x2 - x1 + 1, y2 - y1 + 1)

    def draw_tile_area(self, name     , area                                         ):
        Tileset().draw_tile_size(name, self.canvas, self.start_x + area[0][0], self.start_y + area[0][1], area[1][0] - area[0][0] + 1, area[1][1] - area[0][1] + 1)

    def import_graphic(self, source_g     ,
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
            self.canvas, self.start_x + target_x, self.start_y + target_y, target_width, target_height,
            source_g, source_x, source_y, source_width, source_height)

    def export_graphic(self, target_g     ,
                       source_x=0, source_y=0, source_width=None, source_height=None,
                       target_x=0, target_y=0, target_width=None, target_height=None):
        """
        copy a partial virtual graph "source" into a graph "target"
        """

        source_width = source_width if source_width is not None else self.width
        source_height = source_height if source_height is not None else self.height
        target_width = target_width if target_width is not None else source_width
        target_height = target_height if target_height is not None else source_height

        hpprime.strblit2(
            target_g, target_x, target_y, target_width, target_height,
            self.canvas, self.start_x + source_x, self.start_y + source_y, source_width, source_height)

    def copy_to(self, target_v                  ,
                source_x=0, source_y=0, source_width=None, source_height=None,
                target_x=0, target_y=0, target_width=None, target_height=None):
        """
        copy a partial virtual graph "source" into another virtual graph "target"
        """

        source_width = source_width if source_width is not None else self.width
        source_height = source_height if source_height is not None else self.height
        target_width = target_width if target_width is not None else source_width
        target_height = target_height if target_height is not None else source_height

        hpprime.strblit2(
            target_v.canvas, target_v.start_x + target_x, target_v.start_y + target_y, target_width, target_height,
            self.canvas, self.start_x + source_x, self.start_y + source_y, source_width, source_height)
