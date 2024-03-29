import utils
from canvas import Canvas
import reference
import object_types
import button

try:
    from typing import Optional
except:
    pass

class Room:
    def __init__(self, width, height, id     , color       , fill_with_blocks, not_block, is_void):
        self.width = width
        self.height = height
        self.id = id
        self.color = color  # (hue, saturation, value)
        self.fill_with_blocks = fill_with_blocks
        self.not_block = not_block  # to make the room render even if it is surrounded by walls
        self.is_void = is_void
        self.is_root_room = False
        self.static_is_surrounded = None
        self.exit_reference                                = None
        # coordinates start at 0,0 in the bottom left corner
        self.wall_map = [[False for y in range(height)] for x in range(width)]
        self.reference_map                                            = [[None for y in range(height)] for x in range(width)]
        self.buttons                      = []

    def __str__(self):
        return "Room{}".format(self.id)

    def sub_area(self, area, x, y):
        """
        return the area of the sub room at (x, y)
        """
        size = area[1][0] - area[0][0] + 1, area[1][1] - area[0][1] + 1
        new_pos_left_bottom = (area[0][0] + x * size[0] // self.width,
                               area[0][1] + y * size[1] // self.height)
        new_pos_right_top = (area[0][0] + max((x + 1) * size[0] // self.width - 1, 0),
                             area[0][1] + max((y + 1) * size[1] // self.height - 1, 0))
        return new_pos_left_bottom, new_pos_right_top

    def is_surrounded(self):
        if self.width == 0 and self.height == 0:
            return self.wall_map[0][0]
        # check the top and bottom
        for i in range(self.width):
            if not self.wall_map[i][0]:
                return False
            if not self.wall_map[self.width - i - 1][self.height - 1]:
                return False
        # check the left and right
        for i in range(self.height):
            if not self.wall_map[0][i]:
                return False
            if not self.wall_map[self.width - 1][self.height - i - 1]:
                return False
        return True

    def is_surrounded_by_wall(self):
        if self.static_is_surrounded is None:
            self.static_is_surrounded = self.is_surrounded()
        return self.static_is_surrounded

    def render(self, canvas        , area                                         ,
               render_as_flipped      ):
        """
        area: (left_bottom, right_top), both are (x, y)
        """

        # print("rendering room {}, render size: {} x {}".format(self.id, size[0], size[1]))

        size = area[1][0] - area[0][0] + 1, area[1][1] - area[0][1] + 1
        if size[0] <= 0 or size[1] <= 0:
            return
        elif size[0] <= 5 or size[1] <= 5:
            ground_color = self.color[:2] + (self.color[2] * (0.45 + 0.55 * self.is_surrounded_by_wall()),)
            canvas.draw_filled_box_area(area, utils.Color.hsv_to_rgb_int(*ground_color), 0)
            return

        wall_color_int = utils.Color.hsv_to_rgb_int(*self.color)

        if self.fill_with_blocks or (not self.not_block and self.is_surrounded_by_wall()):
            canvas.draw_filled_box_area(area, wall_color_int, 0)
        else:
            ground_color = self.color[:2] + (self.color[2] * 0.45,)
            canvas.draw_filled_box_area(area, utils.Color.hsv_to_rgb_int(*ground_color), 0)
            for x in range(self.width):
                for y in range(self.height):
                    render_x = self.width - x - 1 if render_as_flipped else x
                    render_y = y
                    inner_area = self.sub_area(area, render_x, self.height - render_y - 1)

                    if canvas.is_area_visible(inner_area):
                        if self.wall_map[x][y]:
                            canvas.draw_filled_box_area(inner_area, wall_color_int)
                        elif self.reference_map[x][y] is not None:
                            inner_reference = self.reference_map[x][y]
                            inner_reference.render(canvas, inner_area, wall_color_int, render_as_flipped)

            for button in self.buttons:
                render_x = self.width - button.pos[0] - 1 if render_as_flipped else button.pos[0]
                render_y = button.pos[1]
                inner_area = self.sub_area(area, render_x, self.height - render_y - 1)
                if canvas.is_area_visible(inner_area):
                    button.render(inner_area, canvas, self.reference_map)

            if self.exit_reference is None or not self.exit_reference.is_nonenterable():
                canvas.draw_empty_box_area(area, 0)
            else:
                canvas.draw_empty_box_area(area, 0xffe700)

    def is_in_bound(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    def is_at_edge(self, pos):
        return pos[0] == 0 or pos[0] == self.width - 1 or pos[1] == 0 or pos[1] == self.height - 1
    
    def is_inside(self, pos):
        return 0 < pos[0] < self.width - 1 and 0 < pos[1] < self.height - 1

    def get(self, pos):
        if self.fill_with_blocks:
            return object_types.WALL
        reference = self.reference_map[pos[0]][pos[1]]
        if reference is not None:
            return reference
        elif self.wall_map[pos[0]][pos[1]]:
            return object_types.WALL
        else:
            return object_types.GROUND

    def is_completed(self):
        for button in self.buttons:
            if not button.is_done(self.reference_map):
                return False
        return True