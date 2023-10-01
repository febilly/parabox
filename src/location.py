import directions
import object_types

try:
    from typing import Optional, TYPE_CHECKING
    if TYPE_CHECKING:
        from reference import Reference
        from room import Room
except:
    pass

class Location:
    def __init__(self, room: "Room", pos: tuple[int, int], offset=0.5, is_flipped=False, relative_scale=(1, 1)):
        self.room = room
        self.pos = pos

        self.offset = offset
        self.is_relatively_flipped = is_flipped  # 相对于移动中的上一个location
        self.relative_scale = relative_scale  # 相对于移动中的上一个location

    def __str__(self):
        return "{} {}".format(self.room, self.pos)

    def __eq__(self, other: "Location"):
        return self.room.id == other.room.id and self.pos == other.pos

    def __hash__(self):
        return hash((self.room.id, self.pos))

    def get_sanitized_location(self) -> "Location":
        """
        返回一个新的只包含room和pos的Location（其他的值都是默认值）
        """
        return Location(self.room, self.pos)


    def is_reference(self) -> bool:
        return self.room.reference_map[self.pos[0]][self.pos[1]] is not None

    def get_type(self) -> int:
        if self.room.reference_map[self.pos[0]][self.pos[1]] is not None:
            if self.room.reference_map[self.pos[0]][self.pos[1]].is_wall:
                return object_types.POSSESSABLE_WALL
            else:
                return object_types.REFERENCE
        elif self.room.wall_map[self.pos[0]][self.pos[1]]:
            return object_types.WALL
        else:
            return object_types.GROUND

    def get_reference(self) -> Optional["Reference"]:
        return self.room.reference_map[self.pos[0]][self.pos[1]]

    def get_next_location(self, direction: int, queried_directions: Optional[dict["Location", int]]=None) -> Optional['Location']:
        # 先检查没有退出方块的情况
        next_pos = directions.next_pos(self.pos, direction)
        if self.room.is_in_bound(next_pos):
            return Location(self.room, next_pos, self.offset, self.is_relatively_flipped, self.relative_scale)

        # 如果无法退出方块就返回None
        elif self.room.exit_reference is None:
            return None

        # 准备退出exit_reference，计算所需的各项参数
        exit_reference = self.room.exit_reference
        if queried_directions is None:
            queried_directions = {}
        queried_directions[self] = direction
        new_direction = directions.reverse(direction) if exit_reference.is_flipped and directions.is_horizontal(
            direction) else direction
        new_scale = (self.relative_scale[0] * self.room.width, self.relative_scale[1] * self.room.height)

        # 计算离开exit_reference后的新offset
        if direction == directions.UP or direction == directions.DOWN:
            new_offset = (self.pos[0] + self.offset) / self.room.width
        else:
            new_offset = (self.pos[1] + self.offset) / self.room.height
        if exit_reference.is_flipped and directions.is_vertical(direction):
            new_offset = 1 - new_offset

        # 计算exit_reference的location
        exit_reference_location = Location(exit_reference.parent_room, exit_reference.pos, new_offset, self.is_relatively_flipped ^ exit_reference.is_flipped, new_scale)

        # 检查是否形成无限退出
        if queried_directions.get(exit_reference_location, None) == new_direction:
            # 触发了无限退出，返回infexit的get_next_location
            this_reference = self.get_reference()
            if this_reference.is_infexit:
                next_degree = this_reference.infexit_num + 1
            else:
                next_degree = 0
            infexit = this_reference.get_infexit_reference(next_degree)
            new_offset = 1 - self.offset if infexit.is_flipped and directions.is_vertical(new_direction) else self.offset
            new_location = Location(infexit.parent_room, infexit.pos, new_offset, infexit.is_flipped, new_scale)
            return new_location.get_next_location(new_direction, queried_directions)

        # 从exit_reference_location出发，寻找下一个方块
        return exit_reference_location.get_next_location(new_direction, queried_directions)

