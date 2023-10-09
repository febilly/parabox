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
    def __init__(self, room        , pos                 , offset=0.5, is_flipped=False, relative_scale=(1, 1), reference                       =None):
        self.room = room
        self.pos = pos

        self.offset = offset
        self.is_relatively_flipped = is_flipped  # ������ƶ��е���һ��location
        self.relative_scale = relative_scale  # ������ƶ��е���һ��location

        self.reference = reference  # ��һroom��None�Ļ�����ֻ�ܴ������ȡreference��

    def __str__(self):
        return "{} {}".format(self.room, self.pos)

    def __eq__(self, other            ):
        return self.room.id == other.room.id and self.pos == other.pos

    def __hash__(self):
        return hash((self.room.id, self.pos))

    @classmethod
    def from_reference(cls, reference, offset=0.5, is_flipped=False, relative_scale=(1, 1)):
        return cls(reference.parent_room, reference.pos, offset, is_flipped, relative_scale, reference)

    def get_sanitized_location(self)              :
        """
        ����һ���µ�ֻ����room��pos��Location��������ֵ����Ĭ��ֵ��
        """
        return Location(self.room, self.pos)


    def is_reference(self)        :
        if self.room is None and self.reference is not None:
            return True
        return self.room.reference_map[self.pos[0]][self.pos[1]] is not None

    def get_type(self)       :
        if self.room is None and self.reference is not None:
            if self.reference.is_wall:
                return object_types.POSSESSABLE_WALL
            else:
                return object_types.REFERENCE

        if self.room.fill_with_blocks:
            return object_types.WALL

        if self.room.reference_map[self.pos[0]][self.pos[1]] is not None:
            if self.room.reference_map[self.pos[0]][self.pos[1]].is_wall:
                return object_types.POSSESSABLE_WALL
            else:
                return object_types.REFERENCE
        elif self.room.wall_map[self.pos[0]][self.pos[1]]:
            return object_types.WALL
        else:
            return object_types.GROUND

    def get_reference(self)                         :
        if self.room is None and self.reference is not None:
            return self.reference
        return self.room.reference_map[self.pos[0]][self.pos[1]]

    def get_next_location(self, direction     , queried_directions                                 =None)                        :
        if self.room is None and self.reference is not None:
            return None

        # �ȼ��û���˳���������
        next_pos = directions.next_pos(self.pos, direction)
        if self.room.is_in_bound(next_pos):
            return Location(self.room, next_pos, self.offset, self.is_relatively_flipped, self.relative_scale)

        # ����޷��˳�����ͷ���None
        elif self.room.exit_reference is None:
            return None

        # ׼���˳�exit_reference����������ĸ������
        exit_reference = self.room.exit_reference
        if queried_directions is None:
            queried_directions = {}
        queried_directions[self] = direction
        new_direction = directions.reverse(direction) if exit_reference.is_flipped and directions.is_horizontal(
            direction) else direction
        new_scale = (self.relative_scale[0] * self.room.width, self.relative_scale[1] * self.room.height)

        # �����뿪exit_reference�����offset
        if direction == directions.UP or direction == directions.DOWN:
            new_offset = (self.pos[0] + self.offset) / self.room.width
        else:
            new_offset = (self.pos[1] + self.offset) / self.room.height
        if exit_reference.is_flipped and directions.is_vertical(direction):
            new_offset = 1 - new_offset

        # ����exit_reference��location
        exit_reference_location = self.from_reference(exit_reference, new_offset, self.is_relatively_flipped ^ exit_reference.is_flipped, new_scale)

        # ����Ƿ��γ������˳�
        if queried_directions.get(exit_reference_location, None) == new_direction:
            # �����������˳�������infexit��get_next_location
            this_reference = self.get_reference()
            if this_reference.is_infexit:
                next_degree = this_reference.infexit_num + 1
            else:
                next_degree = 0
            infexit = this_reference.get_infexit_reference(next_degree)
            new_offset = 1 - self.offset if infexit.is_flipped and directions.is_vertical(new_direction) else self.offset
            new_location = Location(infexit.parent_room, infexit.pos, new_offset, infexit.is_flipped, new_scale)
            return new_location.get_next_location(new_direction, queried_directions)

        # ��exit_reference_location������Ѱ����һ������
        return exit_reference_location.get_next_location(new_direction, queried_directions)
