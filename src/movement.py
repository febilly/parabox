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


class Record:
    def __init__(self, reference: "Reference", new_location: Location, is_player):
        self.reference = reference
        self.new_location = new_location  # 使用new_location里面的room、pos和is_relatively_flipped（和已有的flipped异或）
        self.is_player = is_player

    def __eq__(self, other):
        return self.reference == other.reference and self.new_location == other.new_location

    def __str__(self):
        return "Moving {} to {}".format(self.reference, self.new_location)

class BaseActionNode:
    def __init__(self, location: Location, initiator_location: Optional[Location], direction: int,
                 record_stack: list, is_first_movement: bool):
        """
        初始化时只记录传入的参数，不进行其他操作
        """
        self.location = location
        self.initiator_location = initiator_location
        self.direction = direction
        self.record_stack = record_stack
        self.is_first_movement = is_first_movement
        self.recorded = False

    def __enter__(self):
        """
        进入时，进行一些计算，并对于动作的发起者和接受者进行处理（比如翻转）（假设动作成功执行），以及记录当前的动作
        """
        self.this_reference = self.location.get_reference()
        self.original_pressed_direction = self.this_reference.pressed_direction
        self.this_reference.pressed_direction = self.direction
        self.initiator_reference = self.initiator_location.get_reference() if self.initiator_location is not None else None

    def is_finished(self):
        """
        判断进行当前动作后是否确定动作能够成功完成
        """
        return False

    def expand(self):
        """
        返回下一步可能的动作
        """
        return []

    def __exit__(self, *args):
        """
        退出时，撤销对于动作的发起者和接受者的处理，并删除记录的动作
        """
        if self.recorded:
            self.record_stack.pop()
        self.this_reference.pressed_direction = None

class PushNode(BaseActionNode):
    def __init__(self, location: Location, initiator_location: Optional[Location], direction: int,
                 record_stack: list, is_first_movement: bool):
        super().__init__(location, initiator_location, direction, record_stack, is_first_movement)

    def __enter__(self):
        super().__enter__()
        self.next_location = self.location.get_sanitized_location().get_next_location(self.direction)
        self.next_reference = self.next_location.get_reference() if self.next_location is not None else None
        if self.next_location is not None and self.next_location.is_relatively_flipped:
            self.this_reference.is_flipped ^= True
        self.record_stack.append(Record(self.this_reference, self.next_location, None))
        self.recorded = True

    def is_finished(self):
        return (self.next_location is not None and self.next_location.get_type() == object_types.GROUND) or \
               (self.original_pressed_direction == self.direction)

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
        # 如果是ground的话，按理来说应该已经在判断push的is_finish的时候成功并且返回路径了，所以这里不考虑ground
        if next_location_type == object_types.REFERENCE:
            next_nodes.append(PushNode(self.next_location, self.location, new_direction, self.record_stack, False))
            if not self.next_reference.is_nonenterable():
                next_nodes.append(EnteredByNode(self.next_location, self.location, new_direction, self.record_stack, self.is_first_movement, 0))
            if not (self.this_reference.is_wall or self.this_reference.is_nonenterable()):
                next_nodes.append(EatenByNode(self.next_location, self.location, new_direction, self.record_stack, self.is_first_movement))
        if self.is_first_movement:
            next_nodes.append(PossessedByNode(self.next_location, self.location, new_direction, self.record_stack, self.is_first_movement))

        return next_nodes

    def __exit__(self, *args):
        super().__exit__()
        if self.next_location.is_relatively_flipped:
            self.this_reference.is_flipped ^= True

class EnteredByNode(BaseActionNode):
    def __init__(self, location: Location, initiator_location: Location, direction: int,
                 record_stack: list, is_first_movement: bool, infenter_degree: int):
        super().__init__(location, initiator_location, direction, record_stack, is_first_movement)
        self.infenter_degree = infenter_degree

    def __enter__(self):
        super().__enter__()
        if self.this_reference.is_flipped:
            self.initiator_reference.is_flipped ^= True
        enter_pos = directions.enter_pos(self.direction, self.this_reference.room.width, self.this_reference.room.height, self.location.is_relatively_flipped, self.location.offset)
        if self.this_reference.is_flipped:
            if directions.is_vertical(self.direction):
                self.enterer_direction = self.direction
                inner_offset = 1 - self.location.offset
            else:
                self.enterer_direction = directions.reverse(self.direction)
                inner_offset = self.location.offset
        else:
            self.enterer_direction = self.direction
            inner_offset = self.location.offset
        if directions.is_vertical(self.direction):
            new_offset = inner_offset * self.this_reference.room.width - enter_pos[0]
        else:
            new_offset = inner_offset * self.this_reference.room.height - enter_pos[1]
        self.enter_location = Location(self.this_reference.room, enter_pos, new_offset, self.this_reference.is_flipped, (1 / self.this_reference.room.width, 1 / self.this_reference.room.height))
        self.enter_location_type = self.enter_location.get_type() if self.enter_location is not None else None
        self.enter_reference = self.enter_location.get_reference() if self.enter_location is not None else None
        self.record_stack.append(Record(self.initiator_reference, self.enter_location, None))
        self.recorded = True

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

        if self.enter_location_type == object_types.REFERENCE:
            next_nodes.append(PushNode(self.enter_location, self.initiator_location, self.enterer_direction, self.record_stack, False))
            if not self.enter_reference.is_nonenterable():
                if self.this_reference.room == self.enter_reference.room and self.location.offset == self.enter_location.offset:
                    # 检测到无限进入，将被进入的房间替换为infenter
                    infenter = self.this_reference.get_infenter_reference(self.infenter_degree)
                    infenter_location = Location(infenter.parent_room, infenter.pos, self.location.offset, infenter.is_flipped, (1 / infenter.room.width, 1 / infenter.room.height))  # 其实我举得这里不应该写self.location.offset，但是反正游戏里碰到的无限进入的时候的offset都是0.5，先懒得管这里了
                    next_nodes.append(EnteredByNode(infenter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                      self.is_first_movement, 0))
                else:
                    # 正常进入，不是无限进入
                    next_nodes.append(EnteredByNode(self.enter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                                    self.is_first_movement, 0))
            if not (self.this_reference.is_wall or self.this_reference.is_nonenterable()):
                next_nodes.append(EatenByNode(self.enter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                              self.is_first_movement))
        if self.is_first_movement:
            next_nodes.append(PossessedByNode(self.enter_location, self.initiator_location, self.enterer_direction, self.record_stack,
                                              self.is_first_movement))

        return next_nodes

    def __exit__(self, *args):
        super().__exit__()
        if self.this_reference.is_flipped:
            self.initiator_reference.is_flipped ^= True

class EatenByNode(BaseActionNode):
    """
    eater前进一格，被吃的reference进入eater
    """
    pass

class PossessedByNode(BaseActionNode):
    pass


def dfs(node: BaseActionNode):
    with node:
        if node.is_finished():
            return node.record_stack.copy()
        next_nodes = node.expand()
        for next_node in next_nodes:
            result = dfs(next_node)
            if result is not None:
                return result
        return None

def conduct_record(records: list["Record"], players: dict[int, "Reference"], undo: undo_record.UndoRecord):
    records = records.copy()
    # 寻找可以移动的环
    if records.count(records[-1]) < 2:
        records = records
    else:
        records = records[records.index(records[-1]):-1]

    # 合并同一个reference连续的移动记录
    i = 1
    while i < len(records):
        if records[i].reference is records[i - 1].reference:
            this_location = records[i].new_location
            last_location = records[i - 1].new_location
            this_location.is_relatively_flipped ^= last_location.is_relatively_flipped
            this_location.relative_scale = (this_location.relative_scale[0] * last_location.relative_scale[0], this_location.relative_scale[1] * last_location.relative_scale[1])
            records.pop(i - 1)
        else:
            i += 1

    # record the original state
    # undo.append(undo_record.UndoRecord.Record.from_move_records(records))

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

def push(reference: "Reference", direction: int, players: dict[int, "Reference"], undo_record: undo_record.UndoRecord):
    reference_location = Location(reference.parent_room, reference.pos)
    first_node = PushNode(reference_location, None, direction, [], True)
    record_stack = dfs(first_node)
    if record_stack is not None:
        conduct_record(record_stack, players, undo_record)
