import location
import object_types
from location import Location
import undo_record
import directions

try:
    from typing import Optional, TYPE_CHECKING
    if TYPE_CHECKING:
        from reference import Reference
        from room import Room
except:
    pass

PUSH = 1
ENTER = 2
EAT = 3
POSSESS = 4


class Record:
    def __init__(self, reference             , new_location          , is_player, type):
        self.reference = reference
        self.new_location = new_location  # ʹ��new_location�����room��pos��is_relatively_flipped�������е�flipped���
        self.is_player = is_player
        self.type = type

    def __eq__(self, other):
        return self.reference == other.reference

    def __str__(self):
        return "Moving {} to {}".format(self.reference, self.new_location)

class BaseActionNode:
    def __init__(self, this_location          , initiator_location                    , direction     ,
                 record_stack      , is_first_movement      ):
        """
        ��ʼ��ʱֻ��¼����Ĳ�������������������
        """
        self.this_location = this_location
        self.initiator_location = initiator_location
        self.direction = direction
        self.record_stack = record_stack
        self.is_first_movement = is_first_movement
        self.record_count = 0

    def __enter__(self):
        """
        ����ʱ������һЩ���㣬�����ڶ����ķ����ߺͽ����߽��д������緭ת�������趯���ɹ�ִ�У����Լ���¼��ǰ�Ķ���
        """
        self.this_reference = self.this_location.get_reference()
        self.original_pressed_direction = self.this_reference.pressed_direction
        self.this_reference.pressed_direction = self.direction
        self.initiator_reference = self.initiator_location.get_reference() if self.initiator_location is not None else None

    def is_finished(self):
        """
        �жϽ��е�ǰ�������Ƿ�ȷ�������ܹ��ɹ����
        """
        return False

    def expand(self):
        """
        ������һ�����ܵĶ���
        """
        return []

    def __exit__(self, *args):
        """
        �˳�ʱ���������ڶ����ķ����ߺͽ����ߵĴ�����ɾ����¼�Ķ���
        """
        for _ in range(self.record_count):
            self.record_stack.pop()
        self.this_reference.pressed_direction = self.original_pressed_direction

class PushNode(BaseActionNode):
    def __init__(self, this_location          , initiator_location                    , direction     ,
                 record_stack      , is_first_movement      ):
        super().__init__(this_location, initiator_location, direction, record_stack, is_first_movement)

    def __enter__(self):
        super().__enter__()
        self.next_location = self.this_location.get_sanitized_location().get_next_location(self.direction)
        self.next_reference = self.next_location.get_reference() if self.next_location is not None else None
        if self.next_location is not None and self.next_location.is_relatively_flipped:
            self.this_reference.is_flipped ^= True
        self.record_stack.append(Record(self.this_reference, self.next_location, None, PUSH))
        self.record_count = 1

    def is_finished(self):
        return (self.original_pressed_direction is None and self.next_location is not None and self.next_location.get_type() == object_types.GROUND) or\
               (self.original_pressed_direction == self.direction and self.next_location is not None and self.next_location.get_type() == object_types.REFERENCE)

    def expand(self):
        next_nodes = []
        if self.next_location is None:
            return next_nodes
        next_location_type = self.next_location.get_type()
        if next_location_type == object_types.WALL:
            return next_nodes
        if self.original_pressed_direction is not None and self.original_pressed_direction != self.direction:
            return next_nodes

        new_direction = directions.reverse(self.direction) if self.next_location.is_relatively_flipped and directions.is_horizontal(self.direction) else self.direction
        # �����ground�Ļ���������˵Ӧ���Ѿ����ж�push��is_finish��ʱ��ɹ����ҷ���·���ˣ��������ﲻ����ground
        if next_location_type == object_types.REFERENCE:
            next_nodes.append(PushNode(self.next_location, self.this_location, new_direction, self.record_stack, False))
            if not self.next_reference.is_nonenterable():
                next_nodes.append(EnteredByNode(self.next_location, self.this_location, new_direction, self.record_stack, self.is_first_movement, 0))
            if not (self.this_reference.is_wall or self.this_reference.is_nonenterable()):
                next_nodes.append(EatenByNode(self.next_location, self.this_location, new_direction, self.record_stack, self.is_first_movement))
        if self.is_first_movement:
            next_nodes.append(PossessedByNode(self.next_location, self.this_location, new_direction, self.record_stack, self.is_first_movement))

        return next_nodes

    def __exit__(self, *args):
        super().__exit__()
        if self.next_location.is_relatively_flipped:
            self.this_reference.is_flipped ^= True

class EnteredByNode(BaseActionNode):
    def __init__(self, this_location          , initiator_location          , direction     ,
                 record_stack      , is_first_movement      , infenter_degree     ):
        super().__init__(this_location, initiator_location, direction, record_stack, is_first_movement)
        self.infenter_degree = infenter_degree

    def __enter__(self):
        super().__enter__()
        if self.this_reference.is_flipped:
            self.initiator_reference.is_flipped ^= True
        enter_pos = directions.enter_pos(self.direction, self.this_reference.room.width, self.this_reference.room.height, self.this_reference.is_flipped, self.this_location.offset)
        if self.this_reference.is_flipped:
            if directions.is_vertical(self.direction):
                self.enterer_direction = self.direction
                inner_offset = 1 - self.this_location.offset
            else:
                self.enterer_direction = directions.reverse(self.direction)
                inner_offset = self.this_location.offset
        else:
            self.enterer_direction = self.direction
            inner_offset = self.this_location.offset
        if directions.is_vertical(self.direction):
            new_offset = inner_offset * self.this_reference.room.width - enter_pos[0]
        else:
            new_offset = inner_offset * self.this_reference.room.height - enter_pos[1]
        self.enter_location = Location(self.this_reference.room, enter_pos, new_offset, self.this_reference.is_flipped, (1 / self.this_reference.room.width, 1 / self.this_reference.room.height))
        self.enter_location_type = self.enter_location.get_type() if self.enter_location is not None else None
        self.enter_reference = self.enter_location.get_reference() if self.enter_location is not None else None
        self.record_stack.append(Record(self.initiator_reference, self.enter_location, None, ENTER))
        self.record_count = 1

    def is_finished(self):
        return self.enter_location_type == object_types.GROUND

    def expand(self):
        next_nodes = []
        if self.enter_location is None:
            return next_nodes
        if self.enter_location_type == object_types.WALL:
            return next_nodes
        if self.original_pressed_direction is not None and self.original_pressed_direction != self.direction:
            return next_nodes
        if self.enter_reference.pressed_direction is not None and self.enter_reference.pressed_direction != self.enterer_direction:
            return next_nodes

        sanitised_enter_location = self.enter_location.get_sanitized_location()
        if self.enter_location_type == object_types.REFERENCE:
            next_nodes.append(PushNode(sanitised_enter_location, self.initiator_location, self.enterer_direction, self.record_stack, False))
            if not self.enter_reference.is_nonenterable():
                if self.this_reference.room == self.enter_reference.room and self.this_location.offset == self.enter_location.offset:
                    # ��⵽���޽��룬��������ķ����滻Ϊinfenter
                    infenter = self.this_reference.get_infenter_reference(self.infenter_degree)
                    infenter_location = Location(infenter.parent_room, infenter.pos, self.this_location.offset, infenter.is_flipped, (1 / infenter.room.width, 1 / infenter.room.height), infenter)  # ��ʵ�Ҿٵ����ﲻӦ��дself.location.offset�����Ƿ�����Ϸ�����������޽����ʱ���offset����0.5�������ù�������
                    next_nodes.append(EnteredByNode(infenter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                      self.is_first_movement, self.infenter_degree + 1))
                else:
                    # �������룬�������޽���
                    next_nodes.append(EnteredByNode(self.enter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                                    self.is_first_movement, self.infenter_degree))
            if not (self.initiator_reference.is_wall or self.initiator_reference.is_nonenterable()):
                next_nodes.append(EatenByNode(sanitised_enter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                              self.is_first_movement))
        if self.is_first_movement:
            next_nodes.append(PossessedByNode(sanitised_enter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                              self.is_first_movement))

        return next_nodes

    def __exit__(self, *args):
        super().__exit__()
        if self.this_reference.is_flipped:
            self.initiator_reference.is_flipped ^= True

class EatenByNode(BaseActionNode):
    """
    eaterǰ��һ�񣬱��Ե�reference����eater
    ��Ϊeaterǰ��һ��϶��Ǳ�push�ģ���recordstack�����Ѿ���eater���ƶ���¼�ˣ���������ֻ��Ҫ��¼���Ե�reference����eater���ƶ���¼
    """
    def __init__(self, this_location          , initiator_location                    , direction     ,
                 record_stack      , is_first_movement      ):
        super().__init__(this_location, initiator_location, direction, record_stack, is_first_movement)
        self.is_first_movement = False  # ��Ϊ���Ե�reference������ң�����eat��֮����possess��������ʱ�����Ƕ���ҵ������

    def __enter__(self):
        super().__enter__()
        if self.initiator_reference.is_flipped:
            self.this_reference.is_flipped ^= True
        reversed_direction = directions.reverse(self.direction)
        enter_pos = directions.enter_pos(reversed_direction, self.initiator_reference.room.width, self.initiator_reference.room.height, self.initiator_reference.is_flipped)
        if self.initiator_reference.is_flipped and directions.is_horizontal(reversed_direction):
            self.enterer_direction = directions.reverse(reversed_direction)
        else:
            self.enterer_direction = reversed_direction
        self.this_reference.pressed_direction = self.enterer_direction
        self.enter_location = Location(self.initiator_reference.room, enter_pos, 0.5, self.initiator_reference.is_flipped, (1 / self.initiator_reference.room.width, 1 / self.initiator_reference.room.height))
        self.enter_location_type = self.enter_location.get_type() if self.enter_location is not None else None
        self.enter_reference = self.enter_location.get_reference() if self.enter_location is not None else None
        self.record_stack.append(Record(self.this_reference, self.enter_location, None, EAT))
        self.record_count = 1

    def is_finished(self):
        return self.enter_location_type == object_types.GROUND

    def expand(self):
        next_nodes = []
        if self.enter_location is None:
            return next_nodes
        if self.enter_location_type == object_types.WALL or self.enter_location_type == object_types.POSSESSABLE_WALL:
            return next_nodes

        sanitised_enter_location = self.enter_location.get_sanitized_location()
        next_nodes.append(PushNode(sanitised_enter_location, self.this_location, self.enterer_direction, self.record_stack, False))
        if not self.enter_reference.is_nonenterable():
            if self.initiator_reference.room == self.enter_reference.room:
                # ��⵽���޽��룬��������ķ����滻Ϊinfenter
                if self.initiator_reference.is_infenter:
                    next_degree = self.initiator_reference.infenter_num + 1
                else:
                    next_degree = 0
                infenter = self.initiator_reference.get_infenter_reference(next_degree)
                infenter_location = Location(infenter.parent_room, infenter.pos, self.this_location.offset, infenter.is_flipped, (1 / infenter.room.width, 1 / infenter.room.height), infenter)  # ��ʵ�Ҿٵ����ﲻӦ��дself.location.offset�����Ƿ�����Ϸ�����������޽����ʱ���offset����0.5�������ù�������
                next_nodes.append(EnteredByNode(infenter_location, self.this_location, self.enterer_direction, self.record_stack, self.is_first_movement, next_degree + 1))
            else:
                next_nodes.append(EnteredByNode(sanitised_enter_location, self.this_location, self.enterer_direction, self.record_stack, False, 0))
        # if not (self.initiator_reference.is_wall or self.initiator_reference.is_nonenterable()):
        #     next_nodes.append(EatenByNode(sanitised_enter_location, self.this_location, self.enterer_direction, self.record_stack, False))

        return next_nodes

    def __exit__(self, *args):
        super().__exit__()
        if self.initiator_reference.is_flipped:
            self.this_reference.is_flipped ^= True


class PossessedByNode(BaseActionNode):
    def __init__(self, this_location          , initiator_location                    , direction     ,
                 record_stack      , is_first_movement      ):
        super().__init__(this_location, initiator_location, direction, record_stack, is_first_movement)

    def __enter__(self):
        super().__enter__()
        self.record_stack.append(Record(self.initiator_reference, location.Location.from_reference(self.initiator_reference), False, POSSESS))
        self.record_stack.append(Record(self.this_reference, location.Location.from_reference(self.this_reference), True, POSSESS))
        self.record_count = 2

    def is_finished(self):
        return self.is_first_movement and self.initiator_reference.is_player and not self.this_reference.is_player and self.this_reference.is_possessable

    def expand(self):
        return []

    def __exit__(self, *args):
        super().__exit__()

def dfs(node                ):
    with node:
        if node.is_finished():
            return node.record_stack.copy()
        next_nodes = node.expand()
        for next_node in next_nodes:
            result = dfs(next_node)
            if result is not None:
                return result
        return None

def conduct_record(records                , players                        , undo                        ):
    records = records.copy()

    # �ϲ�ͬһ��reference�������ƶ���¼
    # �����ǰ�������enter���ϲ����������������һ���ʱ���������������enter������ͬһ��movement��������������
    i = 1
    while i < len(records):
        if records[i].type == ENTER and records[i].reference is records[i - 1].reference:
            this_location = records[i].new_location
            last_location = records[i - 1].new_location
            this_location.is_relatively_flipped ^= last_location.is_relatively_flipped
            this_location.relative_scale = (this_location.relative_scale[0] * last_location.relative_scale[0],
                                            this_location.relative_scale[1] * last_location.relative_scale[1])
            records.pop(i - 1)
        else:
            i += 1

    # Ѱ�ҿ����ƶ��Ļ�
    if records.count(records[-1]) < 2:
        records = records
    else:
        records = records[records.index(records[-1]):-1]

    # record the original state
    undo.append(undo_record.UndoRecord.Record.from_move_records(records))

    # conduct
    for record in records:
        reference = record.reference
        new_location = record.new_location

        if reference.float_in_space:
            continue

        # remove reference from old place
        old_pos = reference.pos
        old_map = reference.parent_room.reference_map
        if old_map[old_pos[0]][old_pos[1]] is reference:
            old_map[old_pos[0]][old_pos[1]] = None

        # add reference to new place
        reference.is_flipped ^= new_location.is_relatively_flipped
        if not reference.parent_room == new_location.room:
            reference.is_view_flipped ^= new_location.is_relatively_flipped
        reference.parent_room = new_location.room
        new_pos = new_location.pos
        reference.pos = new_pos
        new_map = reference.parent_room.reference_map
        new_map[new_pos[0]][new_pos[1]] = reference
        if record.is_player is not None:
            if record.is_player:
                players[reference.playerorder] = reference
            reference.is_player = record.is_player

def push(reference             , direction     , players                        , undo_record                        ):
    reference_location = Location(reference.parent_room, reference.pos)
    first_node = PushNode(reference_location, None, direction, [], True)
    record_stack = dfs(first_node)
    if record_stack is not None:
        conduct_record(record_stack, players, undo_record)
