import reference
from virtual_graphic import VirtualGraphic

BUTTON = 1
PLAYER_BUTTON = 2
FAST_TRAVEL = 3
INFO = 4


class Button:
    def __init__(self, pos: tuple[int, int], type, info="") -> None:
        self.pos = pos
        self.type = type
        self.info = info

    def is_done(self, reference_map: list[list[reference.Reference]]):
        reference = reference_map[self.pos[0]][self.pos[1]]
        if self.type == BUTTON:
            return reference is not None and not reference.is_player
        elif self.type == PLAYER_BUTTON:
            return reference is not None and reference.is_player
        else:
            return True

    def render(self, area: tuple[tuple[int, int], tuple[int, int]],
               virtual_graphic: VirtualGraphic, reference_map: list[list[reference.Reference]]):
        if reference_map[self.pos[0]][self.pos[1]] is None:
            if self.type == BUTTON:
                type = "Button"
            elif self.type == PLAYER_BUTTON:
                type = "PlayerButton"
            elif self.type == FAST_TRAVEL:
                type = "FastTravel"
            elif self.type == INFO:
                type = "Info"
            else:
                raise Exception("Unknown button type: {}".format(self.type))
            virtual_graphic.draw_tile_area(type, area)
        elif self.type == PLAYER_BUTTON and reference_map[self.pos[0]][self.pos[1]].is_player:
            virtual_graphic.draw_empty_box_area(area, 0xffffff)
        elif self.type == BUTTON and not reference_map[self.pos[0]][self.pos[1]].is_player:
            virtual_graphic.draw_empty_box_area(area, 0xffffff)
   


